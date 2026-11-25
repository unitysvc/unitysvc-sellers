"""Upload state: what the last ``usvc seller specs upload`` sent, so the next one can skip what has not changed.

A catalog of hundreds of services is re-ingested in full on every run, although most runs change a few of
them, and ingesting an unchanged service still costs a backend task. ``--state FILE`` keeps a record per
service, read at the start of a run and rewritten at the end, so a service whose content has not changed
since it was last ingested is not sent again.

What the record holds, and why:

* ``payload_sha256`` is the fingerprint of the **expanded** content the client would send: provider,
  offering and listing after presets, templates and convenience fields are expanded, with every referenced
  file replaced by the hash of its content (see :class:`unitysvc_sellers.storage.ContentHasher`). It is
  computed locally and without a request. It is not the hash of the authored files, which would miss a
  preset or template change, and it is not what the server stored, which the client cannot see.
* ``ingest`` is the outcome of the ingest task for that payload: ``completed`` (with what the backend did:
  ``created``, ``unchanged``, ``revision_created``, ...) or ``failed``. A payload whose ingest failed was not
  received, so it is never skipped. This is the state of the *upload*, not of the service: the platform
  tests that follow a submission take far too long to wait for, and a service the platform later rejects
  is not re-sent by this tool (re-run its tests, or change it).
* ``test`` is the platform's decision on the service when ``--wait-for-test`` waited for it: ``passed`` (the
  service became ``active`` or ``review``) or not (``rejected``, ``error``, ``timeout``). A service whose
  test did not pass is never skipped, so the next run sends it again. A record without ``test`` was not
  waited for, which is the state of the *upload* only.
* ``service_id`` is the canonical id the backend answered with. If a sidecar names a different one the
  service's identity changed, and it is sent again.

The record is trusted only against the target it was written for, and only while the service still exists
there (``upload`` lists the target's services once, unless told not to).
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATE_VERSION = 1

# What a record's ``test`` says when the platform accepted the service (it became active or review).
TEST_PASSED = "passed"
# A service retired on purpose (deprecated, suspended) is not tested; it has no verdict to remember.
TEST_SKIPPED = "skipped"

# Kinds of upload, one per way ``upload_directory`` sends a service.
KIND_SERVICE = "service"
KIND_SYSTEM = "system"
KIND_PLATFORM = "platform"

_ERROR_LIMIT = 400


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_digest(value: Any) -> str:
    """SHA-256 of ``value`` as canonical JSON (sorted keys, no whitespace)."""
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_target(base_url: str) -> str:
    return (base_url or "").strip().rstrip("/")


def tool_versions() -> dict[str, str]:
    """Versions of the packages that expand and send a payload (informational)."""
    from importlib import metadata

    versions: dict[str, str] = {}
    for package in ("unitysvc-sellers", "unitysvc-core", "unitysvc-data"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            continue
    return versions


def run_context() -> dict[str, str]:
    """Where the run came from, when it is a CI run (informational; never compared)."""
    context: dict[str, str] = {}
    for key, env in (
        ("commit", "GITHUB_SHA"),
        ("run_id", "GITHUB_RUN_ID"),
        ("repository", "GITHUB_REPOSITORY"),
        ("workflow", "GITHUB_WORKFLOW"),
    ):
        value = os.environ.get(env)
        if value:
            context[key] = value
    return context


@dataclass
class ServiceRecord:
    kind: str
    payload_sha256: str
    submitted: bool
    ingest: dict[str, Any]
    service_id: str | None = None
    test: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "kind": self.kind,
            "payload_sha256": self.payload_sha256,
            "submitted": self.submitted,
            "ingest": self.ingest,
        }
        if self.service_id:
            data["service_id"] = self.service_id
        if self.test:
            data["test"] = self.test
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ServiceRecord:
        ingest = data.get("ingest")
        test = data.get("test")
        return cls(
            kind=str(data["kind"]),
            payload_sha256=str(data["payload_sha256"]),
            submitted=bool(data.get("submitted", False)),
            ingest=dict(ingest) if isinstance(ingest, dict) else {},
            service_id=str(data["service_id"]) if data.get("service_id") else None,
            test=dict(test) if isinstance(test, dict) else None,
        )


@dataclass
class UploadState:
    target: str
    services: dict[str, ServiceRecord] = field(default_factory=dict)
    summary: dict[str, int] = field(default_factory=dict)

    # ---- reading and writing ------------------------------------------------

    @classmethod
    def load(cls, path: Path, target: str) -> tuple[UploadState, str | None]:
        """Read ``path``. Returns the state and, when a file existed but was not usable, why it was ignored.

        A missing file is a first run, not an error. A file that cannot be read, is of another version, or
        was written for another target is ignored (every service is sent again) rather than trusted.
        """
        target = normalize_target(target)
        if not path.exists():
            return cls(target=target), None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("not a JSON object")
            if raw.get("version") != STATE_VERSION:
                return cls(target=target), f"it is version {raw.get('version')!r}, this tool writes {STATE_VERSION}"
            if normalize_target(str(raw.get("target", ""))) != target:
                return cls(target=target), f"it was written for {raw.get('target')!r}, not {target!r}"
            services = {
                str(name): ServiceRecord.from_dict(record)
                for name, record in (raw.get("services") or {}).items()
                if isinstance(record, dict)
            }
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return cls(target=target), f"it cannot be read ({exc})"
        return cls(target=target, services=services), None

    def save(self, path: Path) -> None:
        """Write the state atomically (a crash leaves the previous file, not half of the new one)."""
        document = {
            "version": STATE_VERSION,
            "target": self.target,
            "generated_at": now_iso(),
            "context": run_context(),
            "tools": tool_versions(),
            "summary": self.summary,
            "services": {name: record.to_dict() for name, record in sorted(self.services.items())},
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(document, handle, indent=2, sort_keys=False)
                handle.write("\n")
            os.replace(tmp, path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    # ---- the decision -------------------------------------------------------

    def is_current(
        self,
        name: str,
        *,
        kind: str,
        digest: str,
        sidecar_id: str | None,
        submit: bool,
    ) -> bool:
        """Whether ``name`` was ingested with exactly this payload and need not be sent again.

        All of these must hold: a record of the same kind and fingerprint whose ingest completed; it was
        submitted if this run submits (a draft left by an earlier run without ``--submit`` is not
        submitted by skipping it); and the sidecar, when it names an id, names the one the backend answered
        with.
        """
        record = self.services.get(name)
        if record is None or record.kind != kind or record.payload_sha256 != digest:
            return False
        if record.ingest.get("status") != "completed":
            return False
        if submit and not record.submitted:
            return False
        if record.test is not None and record.test.get("status") != TEST_PASSED:
            return False
        return not (sidecar_id and record.service_id and sidecar_id != record.service_id)

    # ---- recording ----------------------------------------------------------

    def record_completed(
        self,
        name: str,
        *,
        kind: str,
        digest: str,
        submitted: bool,
        outcome: str | None,
        service_id: str | None,
        revision_of: str | None = None,
    ) -> None:
        ingest: dict[str, Any] = {"status": "completed", "at": now_iso()}
        if outcome:
            ingest["outcome"] = outcome
        if revision_of:
            ingest["revision_of"] = revision_of
        self.services[name] = ServiceRecord(
            kind=kind,
            payload_sha256=digest,
            submitted=submitted,
            ingest=ingest,
            service_id=service_id,
        )

    def record_failed(self, name: str, *, kind: str, digest: str, submitted: bool, error: str) -> None:
        # The previous canonical id is kept: a failure does not change which service this is.
        previous = self.services.get(name)
        self.services[name] = ServiceRecord(
            kind=kind,
            payload_sha256=digest,
            submitted=submitted,
            ingest={"status": "failed", "at": now_iso(), "error": error[:_ERROR_LIMIT]},
            service_id=previous.service_id if previous else None,
        )

    def record_test(self, name: str, *, status: str, detail: str | None = None) -> None:
        """Record the platform's decision on ``name`` after ``--wait-for-test`` waited for it."""
        record = self.services.get(name)
        if record is None:
            return
        test: dict[str, Any] = {"status": status, "at": now_iso()}
        if detail:
            test["detail"] = detail[:_ERROR_LIMIT]
        record.test = test

    def forget(self, name: str) -> None:
        self.services.pop(name, None)

    def prune(self, keep: set[str]) -> int:
        """Drop the records of services no longer in the catalog. Returns how many."""
        gone = [name for name in self.services if name not in keep]
        for name in gone:
            del self.services[name]
        return len(gone)
