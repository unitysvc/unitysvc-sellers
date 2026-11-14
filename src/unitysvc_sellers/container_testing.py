"""Derived container connectivity tests, using core's compiler and local Docker.

Only explicit container channels take this path. No host files, Docker socket,
host environment, or platform credentials are mounted into seller containers.
"""

from __future__ import annotations

import secrets
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx
from unitysvc_core.instance_spec import compile_instance_spec, validate_instance_spec
from unitysvc_core.models.channel import ContainerChannel
from unitysvc_core.models.container import ContainerEntry, parse_quantity
from unitysvc_core.models.manifest import ManifestService
from unitysvc_core.models.probes import Probe, ProbesV1

from .utils import find_files_by_pattern, service_name_matches

INSTANCE_KEY_REFERENCE = "${UNITYSVC_INSTANCE_API_KEY}"


def _docker(*args: str, timeout: float = 120, check: bool = True) -> str:
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        # Do not interpolate the command line: it may include an app's config.
        raise RuntimeError(f"Docker {args[0]} failed: {result.stderr[-1000:]}")
    return result.stdout.strip()


def _port(container: str, port: int) -> str:
    address = _docker("port", container, f"{port}/tcp").splitlines()[0]
    return f"http://{address}"


def _ready(service: ManifestService, container: str) -> bool:
    if _docker("inspect", "--format", "{{.State.Running}}", container) != "true":
        return False
    health = service.health
    timeout = health.timeout_seconds or 2 if health else 2
    if health and health.type == "exec":
        result = subprocess.run(
            ["docker", "exec", container, *(health.command or [])],
            capture_output=True,
            timeout=timeout,
        )
        return result.returncode == 0
    if not service.ports:
        return True
    port = health.port if health and health.port else service.ports[0]
    address = _port(container, port)
    if health and health.type == "http":
        response = httpx.get(address + (health.path or "/"), timeout=timeout, follow_redirects=False)
        return 200 <= response.status_code < 400
    parsed = urlsplit(address)
    with socket.create_connection((parsed.hostname, parsed.port), timeout=timeout):
        return True


def test_container(source: str, channel: ContainerChannel, probes: ProbesV1 | None = None) -> list[str]:
    """Pull, start, wait for health, probe entries, then remove every resource.

    Local Docker checks the same normalized services and health commands as
    compute. It does not claim to reproduce Kubernetes/gVisor or disk quotas.
    """
    report = validate_instance_spec(source, channel=channel)
    if not report.ok:
        raise ValueError("; ".join(str(issue) for issue in report.errors))
    compiled = compile_instance_spec(source, channel.resources)
    entries = {entry.name: entry for entry in channel.entries or []}
    if any(probe.entry not in entries for probe in (probes.probes if probes else [])):
        raise ValueError("A connectivity probe names an entry missing from this channel")
    network = "usvc-test-" + secrets.token_hex(6)
    app_key = secrets.token_urlsafe(32)
    containers: dict[str, str] = {}
    messages: list[str] = []
    created_network = False
    try:
        # Resolve/validate every environment before making any Docker changes.
        environments: dict[str, dict[str, str]] = {}
        for service in compiled.manifest.services:
            env = {name: value.replace(INSTANCE_KEY_REFERENCE, app_key) for name, value in (service.env or {}).items()}
            if any("${" in value or "\n" in value or "\r" in value for value in env.values()):
                raise ValueError("Local container tests require resolved, single-line environment values")
            environments[service.name] = env
        for service in compiled.manifest.services:
            _docker("pull", service.image, timeout=300)
        _docker("network", "create", network)
        created_network = True
        with tempfile.TemporaryDirectory(prefix="usvc-container-env-") as temporary:
            for service in compiled.manifest.services:
                container = f"{network}-{service.name}"
                env_file = Path(temporary) / service.name
                env_file.write_text("".join(f"{key}={value}\n" for key, value in environments[service.name].items()))
                env_file.chmod(0o600)
                args = [
                    "run",
                    "--detach",
                    "--name",
                    container,
                    "--network",
                    network,
                    "--network-alias",
                    service.name,
                    "--no-healthcheck",
                    "--env-file",
                    str(env_file),
                    "--cap-drop",
                    "ALL",
                    "--security-opt",
                    "no-new-privileges:true",
                ]
                limits = service.resources.limits if service.resources else None
                if limits:
                    args += ["--cpus", str(float(parse_quantity(limits["cpu"])))]
                    args += ["--memory", str(int(parse_quantity(limits["memory"])))]
                for port in service.ports or []:
                    args += ["--publish", f"127.0.0.1::{port}"]
                if service.command:
                    args += ["--entrypoint", service.command[0]]
                args += [service.image]
                if service.command:
                    args += service.command[1:]
                args += service.args or []
                # Track before run: Docker can create the container then fail to start it.
                containers[service.name] = container
                _docker(*args)
            deadline = time.monotonic() + 120
            pending = {service.name: service for service in compiled.manifest.services}
            while pending:
                for name, service in list(pending.items()):
                    try:
                        if _ready(service, containers[name]):
                            del pending[name]
                            messages.append(f"{name}: ready")
                    except (OSError, httpx.HTTPError, subprocess.TimeoutExpired):
                        pass
                if not pending:
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError(f"Readiness timed out for {', '.join(pending)}")
                time.sleep(1)
            with httpx.Client(timeout=10, follow_redirects=False) as client:
                checks: list[tuple[ContainerEntry, str, Probe | None]] = [
                    (entry, entry.path or "/", None) for entry in entries.values()
                ]
                checks += [(entries[probe.entry], probe.path, probe) for probe in (probes.probes if probes else [])]
                for entry, path, probe in checks:
                    headers = {"Authorization": f"Bearer {app_key}"} if entry.auth == "app" else {}
                    response = client.get(_port(containers[entry.service], entry.port) + path, headers=headers)
                    expected = probe.expect_status if probe else None
                    matches = (
                        response.status_code == expected if expected is not None else 200 <= response.status_code < 400
                    )
                    if not matches:
                        raise RuntimeError(f"{entry.name}{path}: unexpected HTTP {response.status_code}")
                    if probe and probe.expect_body_contains and probe.expect_body_contains not in response.text:
                        raise RuntimeError(f"{entry.name}{path}: expected response text was absent")
                    messages.append(f"{entry.name}{path}: HTTP {response.status_code}")
        return messages
    except Exception as exc:
        # Even a badly behaved image cannot write the temporary key to persisted CLI output.
        raise RuntimeError(str(exc).replace(app_key, "[instance key]")) from None
    finally:
        original = sys.exception()
        cleanup_errors: list[str] = []
        for container in containers.values():
            try:
                _docker("rm", "--force", container)
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                cleanup_errors.append(str(exc))
        if created_network:
            try:
                _docker("network", "rm", network)
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                cleanup_errors.append(str(exc))
        if cleanup_errors:
            message = "Docker cleanup failed: " + "; ".join(cleanup_errors)
            if original:
                message += f"; test failure: {original}"
            raise RuntimeError(message.replace(app_key, "[instance key]")) from None


def run_container_tests(data_dir: Path, name: str | None) -> list[dict[str, Any]]:
    """The CLI's derived connectivity rows, one per container channel."""
    results: list[dict[str, Any]] = []
    for listing_file, _, listing in find_files_by_pattern(data_dir, "listing_v1"):
        service_name = listing.get("name", "")
        if name is not None and not service_name_matches(service_name, name):
            continue
        offerings = find_files_by_pattern(listing_file.parent, "offering_v1")
        if not offerings:
            continue
        offering = offerings[0][2]
        for channel_name, raw in (offering.get("upstream_access_config") or {}).items():
            if not isinstance(raw, dict) or raw.get("access_method") != "container":
                continue
            outcome: dict[str, Any] = {"success": False, "exit_code": 1, "stdout": "", "stderr": ""}
            try:
                channel = ContainerChannel.model_validate(raw)
                document = offering["documents"][channel.spec]
                source = (listing_file.parent / document["file_path"]).read_text()
                probes = []
                for document in (listing.get("documents") or {}).values():
                    path = document.get("file_path", "")
                    channels = (document.get("meta") or {}).get("channels")
                    if document.get("category") != "connectivity_test" or not path.endswith(".json"):
                        continue
                    if channels and channel_name not in channels:
                        continue
                    probes.extend(ProbesV1.model_validate_json((listing_file.parent / path).read_text()).probes)
                messages = test_container(source, channel, ProbesV1(probes=probes) if probes else None)
                outcome.update(success=True, exit_code=0, stdout="\n".join(messages))
            except Exception as exc:
                outcome.update(error=str(exc), stderr=str(exc))
            results.append(
                {
                    "service_name": service_name,
                    "provider": service_name.split("/")[0],
                    "title": "Container connectivity",
                    "channel": channel_name,
                    "category": "connectivity_test",
                    "listing_file": listing_file,
                    "result": outcome,
                }
            )
    return results
