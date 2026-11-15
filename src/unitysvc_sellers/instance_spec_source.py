"""Find an offering's single instance spec and, for a URL, fetch it locally.

An offering has exactly one instance spec (unitysvc/unitysvc-core#107): the
offering-level ``instance_spec`` shortcut, or one Document of category
``instance_spec``. Either may be a relative path or an https URL.

Upload never downloads a URL: the backend snapshots it at ingest. This module
is only for the seller's local checks (``specs validate`` and the Docker
``run-tests``), which need the bytes. The download goes to memory or a temp
dir, never into the seller's tree, and is refused unless it is https (on every
redirect hop too), small, quick and, when the Document pins ``meta.sha256``,
byte-identical to what was tested. This runs on the seller's own machine; the
backend does its own fetch and SSRF checks at upload, so none are repeated here.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx
from unitysvc_core.instance_spec import INSTANCE_SPEC_TITLE

MAX_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 15.0
MAX_REDIRECTS = 3

_GITHUB_BLOB = re.compile(r"^/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<ref>[^/]+)/(?P<path>.+)$")
_COMMIT_SHA = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")


class InstanceSpecFetchError(ValueError):
    """The spec URL cannot be used (refused, unreachable, too large or not what was pinned)."""


@dataclass
class InstanceSpecSource:
    """The offering's one instance spec: where it is, and (once read) its text."""

    title: str
    document: dict[str, Any]
    text: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def url(self) -> str | None:
        value = self.document.get("external_url")
        return value if isinstance(value, str) and value else None

    @property
    def is_remote(self) -> bool:
        return self.url is not None


def find_instance_spec(offering: dict[str, Any] | None) -> InstanceSpecSource | None:
    """The offering's one instance spec (the shortcut, else the Document), or ``None``.

    ``None`` when there is none or more than one: the offering model reports those.
    """
    if not isinstance(offering, dict):
        return None
    documents = offering.get("documents")
    found = [
        (title, doc)
        for title, doc in (documents if isinstance(documents, dict) else {}).items()
        if isinstance(doc, dict) and doc.get("category") == "instance_spec"
    ]
    shortcut = offering.get("instance_spec")
    if isinstance(shortcut, str) and shortcut:
        key = "external_url" if "://" in shortcut else "file_path"
        found.append((INSTANCE_SPEC_TITLE, {"category": "instance_spec", key: shortcut}))
    if len(found) != 1:
        return None
    return InstanceSpecSource(title=found[0][0], document=found[0][1])


def instance_spec_environment(source: InstanceSpecSource) -> dict[str, dict[str, str]] | None:
    """The Document's ``meta.environment`` overlay (``{service: {NAME: value}}``), for core to merge at compile time."""
    meta = source.document.get("meta")
    overlay = meta.get("environment") if isinstance(meta, dict) else None
    return overlay if isinstance(overlay, dict) else None


def raw_github_url(url: str) -> str:
    """Rewrite a ``github.com/<o>/<r>/blob/<ref>/<path>`` page to ``raw.githubusercontent.com``."""
    parts = urlsplit(url)
    if (parts.hostname or "").lower() != "github.com":
        return url
    match = _GITHUB_BLOB.match(parts.path)
    if not match:
        return url
    return f"https://raw.githubusercontent.com/{match['owner']}/{match['repo']}/{match['ref']}/{match['path']}"


def branch_warning(url: str) -> str | None:
    """A warning when a GitHub raw URL names a branch, which can change under the seller."""
    parts = urlsplit(url)
    if (parts.hostname or "").lower() != "raw.githubusercontent.com":
        return None
    segments = parts.path.split("/")
    if len(segments) < 5:
        return None
    ref = segments[3]
    if _COMMIT_SHA.match(ref):
        return None
    return (
        f"{url} names {ref!r}, which looks like a branch or tag, not a commit SHA: it can change after you "
        "test it. Use a commit permalink (and set meta.sha256 to pin the bytes)"
    )


def _check_https(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise InstanceSpecFetchError(f"instance spec URL {url!r} must be an https URL")


def fetch_instance_spec(
    url: str,
    *,
    sha256: str | None = None,
    max_bytes: int = MAX_BYTES,
    timeout: float = TIMEOUT_SECONDS,
    max_redirects: int = MAX_REDIRECTS,
    transport: httpx.BaseTransport | None = None,
) -> tuple[str, list[str]]:
    """Download an instance spec for a local check; return ``(text, warnings)``.

    https only, at most ``max_bytes``, ``timeout`` per request and
    ``max_redirects`` redirects, each of which must stay https. A GitHub ``blob`` page is
    rewritten to its raw URL. ``sha256`` (the Document's ``meta.sha256``) is
    verified when set. ``transport`` exists for tests.
    """
    current = raw_github_url(url)
    warnings: list[str] = []
    if (note := branch_warning(current)) is not None:
        warnings.append(note)
    body = b""
    with httpx.Client(timeout=timeout, follow_redirects=False, transport=transport) as client:
        for _ in range(max_redirects + 1):
            _check_https(current)
            try:
                with client.stream("GET", current, headers={"Accept": "text/plain, */*;q=0.5"}) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            raise InstanceSpecFetchError(f"{current} redirected without a location")
                        current = urljoin(current, location)
                        continue
                    if response.status_code != 200:
                        raise InstanceSpecFetchError(f"{current} returned HTTP {response.status_code}")
                    declared = response.headers.get("content-length")
                    if declared and declared.isdigit() and int(declared) > max_bytes:
                        raise InstanceSpecFetchError(f"{current} is larger than {max_bytes} bytes")
                    chunks: list[bytes] = []
                    total = 0
                    for chunk in response.iter_bytes():
                        total += len(chunk)
                        if total > max_bytes:
                            raise InstanceSpecFetchError(f"{current} is larger than {max_bytes} bytes")
                        chunks.append(chunk)
                    body = b"".join(chunks)
                    break
            except httpx.HTTPError as exc:
                raise InstanceSpecFetchError(f"cannot download {current}: {exc}") from exc
        else:
            raise InstanceSpecFetchError(f"{url} redirected more than {max_redirects} times")
    if sha256 is not None and hashlib.sha256(body).hexdigest() != sha256:
        raise InstanceSpecFetchError(f"the file at {url} does not match meta.sha256 {sha256}")
    try:
        return body.decode("utf-8"), warnings
    except UnicodeDecodeError:
        raise InstanceSpecFetchError(f"{url} is not UTF-8 text") from None


def read_instance_spec(source: InstanceSpecSource, service_dir: Path, **fetch_options: Any) -> InstanceSpecSource:
    """Fill ``source.text`` from the file next to the offering, or by downloading the URL.

    Raises ``InstanceSpecFetchError`` for a URL that cannot be used, and
    ``ValueError`` for a missing or unreadable local file.
    """
    document = source.document
    if source.url is not None:
        raw_meta = document.get("meta")
        meta: dict[str, Any] = raw_meta if isinstance(raw_meta, dict) else {}
        pinned = meta["sha256"] if isinstance(meta.get("sha256"), str) else None
        source.text, notes = fetch_instance_spec(source.url, sha256=pinned, **fetch_options)
        source.warnings.extend(notes)
    elif isinstance(document.get("file_content"), str):
        source.text = document["file_content"]
    elif isinstance(document.get("file_path"), str):
        path = service_dir / document["file_path"]
        try:
            source.text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError(f"cannot read instance spec {document['file_path']!r}: {exc}") from exc
    else:
        raise ValueError(f"instance spec {source.title!r} has no file_path or external_url")
    return source


def check_remote_instance_spec(offering: dict[str, Any] | None, **fetch_options: Any) -> tuple[list[str], list[str]]:
    """Validate a URL instance spec the way core validates a local one; return ``(errors, warnings)``.

    Core fetches nothing, so for a URL the seller tooling downloads the file
    (see :func:`fetch_instance_spec`) and runs core's validation against every
    container channel. A local spec, or an offering with no container channel,
    has nothing to do here: core already checked it.
    """
    from unitysvc_core.instance_spec import instance_spec_format, validate_instance_spec
    from unitysvc_core.models.channel import ContainerChannel

    source = find_instance_spec(offering)
    configured = (offering or {}).get("upstream_access_config")
    channels = {
        name: raw
        for name, raw in (configured.items() if isinstance(configured, dict) else ())
        if isinstance(raw, dict) and raw.get("access_method") == "container"
    }
    if source is None or not source.is_remote or not channels:
        return [], []
    errors: list[str] = []
    try:
        read_instance_spec(source, Path("."), **fetch_options)
    except ValueError as exc:
        return [f"instance spec {source.title!r}: {exc}"], source.warnings
    assert source.text is not None
    warnings = list(source.warnings)
    meta = source.document.get("meta")
    fmt = instance_spec_format(meta if isinstance(meta, dict) else None)
    for name, raw in channels.items():
        try:
            channel = ContainerChannel.model_validate(raw)
        except ValueError:
            continue  # the channel's own errors are reported by the schema checks
        report = validate_instance_spec(
            source.text, format=fmt, channel=channel, environment=instance_spec_environment(source)
        )
        at = f"upstream_access_config.{name}"
        errors.extend(f"{at}.instance_spec ({source.title!r}): {issue}" for issue in report.errors)
        warnings.extend(f"{at}: {issue}" for issue in report.warnings)
    return errors, warnings
