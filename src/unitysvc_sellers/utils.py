"""Seller-specific utility functions.

This module contains utilities that encode seller-catalog file layout
conventions (directory structure with providers/services/, convenience
fields like ``logo``/``terms_of_service`` that expand to documents,
Jinja2 template rendering for seller catalogs, and execution of example
scripts for seller-run connectivity tests).

Generic file helpers (hashing, mime types, JSON/TOML loading, override
files, schema-based file discovery, deep-merge) are re-exported from
``unitysvc_core.utils`` for convenience, so seller code can do::

    from unitysvc_sellers.utils import find_files_by_schema, resolve_provider_name

without caring whether a given helper is core or seller-specific.
"""

from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
from typing import Any

from jinja2 import Environment as JinjaEnvironment

# Re-exports from unitysvc_core so seller modules can import everything
# from a single place. ``load_data_file`` and the file-discovery helpers
# that flow through it now handle ``$doc_preset`` / ``$file_preset``
# sentinel expansion transparently — see unitysvc_core.utils and the
# ``@preset`` decorator in unitysvc_data for the full story.
from unitysvc_core.utils import (  # noqa: F401
    compute_file_hash,
    deep_merge_dicts,
    find_data_files,
    find_files_by_schema,
    generate_content_based_key,
    get_basename,
    get_file_extension,
    load_data_file,
    mime_type_to_extension,
    write_data_file,
)


def service_name_matches(service_name: str | None, pattern: str) -> bool:
    """Return True if ``service_name`` matches a ``--name`` pattern.

    The CLI accepts shell-style wildcards against ``service_name`` (=
    ``listing.name``, #1138).  A literal name matches exactly one service;
    ``cohere/*`` (or ``cohere/%`` — see below) matches a set.

    **``%`` is a synonym for ``*``** so operators can type the pattern
    unquoted in a shell — the unix shell would glob-expand ``cohere/*``
    against the local filesystem, but ``cohere/%`` is shell-safe.  Both
    glyphs are platform-illegal in real service names (#1138's grammar
    only permits ``[a-zA-Z0-9._-]``) so this alias loses nothing.

    Matching is **case-sensitive and platform-independent**
    (``fnmatchcase``), and ``*`` spans ``/`` so ``cohere/*`` also matches
    hierarchical names like ``cohere/v1/foo``.
    """
    if not service_name:
        return False
    return fnmatch.fnmatchcase(service_name, pattern.replace("%", "*"))


def literal_pattern_prefix(pattern: str) -> str | None:
    """Return the literal prefix of an fnmatch pattern, before the first wildcard.

    Used to narrow a server-side partial-name search before fnmatch-filtering
    client-side: ``cohere/command-*`` → ``cohere/command-``; ``*llama*`` → None.

    ``%`` is treated as a synonym for ``*`` (see ``service_name_matches``);
    ``cohere/command-%`` also returns ``cohere/command-``.
    """
    out: list[str] = []
    for ch in pattern:
        if ch in "*?[%":
            break
        out.append(ch)
    return "".join(out) or None


def resolve_provider_name(file_path: Path) -> str | None:
    """
    Resolve the provider name for an offering/listing file.

    In the flat ``specs/`` layout every service folder is self-contained, so
    ``provider.{json,toml}`` is a sibling of the offering/listing. Return its
    ``name``.

    Args:
        file_path: Path to the service offering or listing file

    Returns:
        Provider name if a sibling provider file is found, None otherwise
    """
    provider_file = file_path.parent / "provider.json"
    if not provider_file.is_file():
        provider_file = file_path.parent / "provider.toml"
    if not provider_file.is_file():
        return None
    try:
        data, _file_format = load_data_file(provider_file)
        return data.get("name")
    except Exception:
        return None


def resolve_service_name_for_listing(listing_file: Path, listing_data: dict[str, Any] | None = None) -> str | None:
    """
    Resolve the service name for a listing file.

    Finds the offering file in the same directory and returns its name.
    Each service directory must have exactly one offering file.

    Args:
        listing_file: Path to the listing file
        listing_data: Unused, kept for backwards compatibility

    Returns:
        Service name if found, None otherwise
    """
    listing_dir = listing_file.parent

    # Find the service offering file (by filename) in the same directory.
    for data_file in find_data_files(listing_dir):
        if data_file.stem != "offering":
            continue
        try:
            data, _file_format = load_data_file(data_file)
            return data.get("name")
        except Exception:
            continue

    # No offering file found
    return None


def read_service_data(service_dir: Path) -> dict[str, Any] | None:
    """Return the full identity record in ``<service_dir>/service.json``.

    This is the ServiceData structure the backend returns from ingest and the
    seller replays as the ``service_data`` upload field — the *other half* of a
    service's data, kept beside the spec files rather than merged into the
    listing. Returns ``None`` when the file is absent or unreadable.
    """
    service_file = service_dir / "service.json"
    if not service_file.is_file():
        return None
    try:
        data = json.loads(service_file.read_text())
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def read_service_id(service_dir: Path) -> str | None:
    """Return just the ``service_id`` from ``<service_dir>/service.json``."""
    data = read_service_data(service_dir)
    sid = data.get("service_id") if data else None
    return str(sid) if sid else None


def write_service_data(service_dir: Path, record: dict[str, Any]) -> None:
    """Persist the backend's returned identity record into ``service.json``.

    Merges onto any existing file (keys in ``record`` win, others preserved)
    so re-uploads keep prior provenance. ``None`` values in ``record`` are
    dropped so the file stays lean.
    """
    service_file = service_dir / "service.json"
    data: dict[str, Any] = {}
    if service_file.is_file():
        try:
            loaded = json.loads(service_file.read_text())
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}
    data.update({k: v for k, v in record.items() if v is not None})
    service_file.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_service_id(service_dir: Path, service_id: str) -> None:
    """Round-trip just a ``service_id`` into ``service.json`` (other keys kept)."""
    write_service_data(service_dir, {"service_id": str(service_id)})


def read_local_service_ids(data_dir: Path, provider: str | None = None) -> list[str]:
    """Collect backend ``service_id``s for the local services under ``data_dir``.

    The shared ``-l`` / ``--local-ids`` resolution used across the ``services``
    command family: walk every ``listing_v1`` file beneath ``data_dir`` and read
    the backend-assigned id from the sibling ``service.json`` (the flat
    ``specs/`` layout keeps the id as provenance beside the spec files). Folders
    without a recorded id are skipped.

    With ``provider`` set, keep only services whose sibling ``provider_v1``
    ``name`` contains the given substring (case-insensitive) — matching the
    filter the bulk ``services`` commands apply in ``--local-ids`` mode.
    """
    provider_lower = provider.lower() if provider else None
    ids: list[str] = []
    for listing_path, _fmt, _data in find_files_by_schema(data_dir, "listing_v1"):
        sid = read_service_id(listing_path.parent)
        if not sid:
            continue
        if provider_lower is not None:
            # The provider lives beside the listing in the flat layout.
            prov = find_files_by_schema(listing_path.parent, "provider_v1")
            prov_name = (prov[0][2].get("name") or "") if prov else ""
            if provider_lower not in prov_name.lower():
                continue
        ids.append(sid)
    return ids


def convert_convenience_fields_to_documents(
    data: dict[str, Any],
    base_path: Path,
    *,
    logo_field: str = "logo",
    terms_field: str | None = "terms_of_service",
) -> dict[str, Any]:
    """
    Convert convenience fields (logo, terms_of_service) to Document objects.

    This utility function converts file paths or URLs in convenience fields
    to proper Document structures that can be stored in the backend.

    Args:
        data: Data dictionary containing potential convenience fields
        base_path: Base path for resolving relative file paths
        logo_field: Name of the logo field (default: "logo")
        terms_field: Name of the terms of service field (default: "terms_of_service", None to skip)

    Returns:
        Updated data dictionary with convenience fields converted to documents dict

    Example:
        >>> data = {"logo": "assets/logo.png", "documents": {}}
        >>> result = convert_convenience_fields_to_documents(data, Path("/data/provider"))
        >>> # Result will have logo removed and added to documents dict
    """
    # Initialize documents dict if not present
    if "documents" not in data or data["documents"] is None:
        data["documents"] = {}

    # Helper to determine MIME type from file path/URL
    def get_mime_type(path_or_url: str) -> str:
        path_lower = path_or_url.lower()
        if path_lower.endswith((".png", ".jpg", ".jpeg")):
            return "png" if ".png" in path_lower else "jpeg"
        elif path_lower.endswith(".svg"):
            return "svg"
        elif path_lower.endswith(".pdf"):
            return "pdf"
        elif path_lower.endswith(".md"):
            return "markdown"
        else:
            # Default to URL if it looks like a URL, otherwise markdown
            return "url" if path_or_url.startswith("http") else "markdown"

    # Convert logo field
    if logo_field in data and data[logo_field]:
        logo_value = data[logo_field]
        logo_doc: dict[str, Any] = {
            "category": "logo",
            "mime_type": get_mime_type(str(logo_value)),
            "is_public": True,
        }

        # Check if it's a URL or file path
        if str(logo_value).startswith("http"):
            logo_doc["external_url"] = str(logo_value)
        else:
            # It's a file path - will be resolved by resolve_file_references
            logo_doc["file_path"] = str(logo_value)

        data["documents"]["Company Logo"] = logo_doc
        # Remove the convenience field
        del data[logo_field]

    # Convert terms_of_service field if specified
    if terms_field and terms_field in data and data[terms_field]:
        terms_value = data[terms_field]
        terms_doc: dict[str, Any] = {
            "category": "terms_of_service",
            "mime_type": get_mime_type(str(terms_value)),
            "is_public": True,
        }

        # Check if it's a URL or file path
        if str(terms_value).startswith("http"):
            terms_doc["external_url"] = str(terms_value)
        else:
            # It's a file path - will be resolved by resolve_file_references
            terms_doc["file_path"] = str(terms_value)

        data["documents"]["Terms of Service"] = terms_doc
        # Remove the convenience field
        del data[terms_field]

    return data


def render_template_file(
    file_path: Path,
    listing: dict[str, Any] | None = None,
    offering: dict[str, Any] | None = None,
    provider: dict[str, Any] | None = None,
    seller: dict[str, Any] | None = None,
    interface: dict[str, Any] | None = None,
    local_testing: bool = False,
    **extra_context: Any,
) -> tuple[str, str]:
    """Render a Jinja2 template file and return content and new filename.

    If the file is not a template (.j2 extension), returns the file content as-is
    and the original filename.

    Args:
        file_path: Path to the file (may or may not be a .j2 template)
        listing: Listing data for template rendering (optional)
        offering: Offering data for template rendering (optional)
        provider: Provider data for template rendering (optional)
        seller: Seller data for template rendering (optional)
        interface: AccessInterface data for template rendering (optional, contains base_url, routing_key, etc.)
        local_testing: When True, signals that the template is being rendered for a local
            test run (``usvc_seller specs run-tests``).  Templates can use ``{% if local_testing %}``
            blocks to include request parameters that must be supplied directly to the
            upstream (no gateway / set_body transformer).  When False (default), templates
            render the clean, user-facing version where the gateway injects parameters from
            the enrollment automatically.
        **extra_context: Additional top-level Jinja2 variables.  ``run-tests`` uses this to
            spread the upstream interface fields (``service_base_url``, ``routing_key``,
            ``host``, ``region``, …) directly into the render namespace so unitysvc-data
            v0.1.7+ templates resolve identically to gateway-side rendering.

    Returns:
        Tuple of (rendered_content, new_filename_without_j2)

    Raises:
        Exception: If template rendering fails
    """
    # Read file content
    with open(file_path, encoding="utf-8") as f:
        file_content = f.read()

    # Check if this is a Jinja2 template
    is_template = file_path.name.endswith(".j2")

    if is_template:
        # Build a Jinja2 environment with a tojson filter so templates can
        # serialise dicts to JSON strings (e.g. ops_testing_parameters).
        env = JinjaEnvironment()
        env.filters["tojson"] = json.dumps

        template = env.from_string(file_content)
        rendered_content = template.render(
            listing=listing or {},
            offering=offering or {},
            provider=provider or {},
            seller=seller or {},
            interface=interface or {},
            local_testing=local_testing,
            **extra_context,
        )

        # Strip .j2 from filename
        # Example: test.py.j2 -> test.py
        new_filename = file_path.name[:-3]  # Remove last 3 characters (.j2)

        return rendered_content, new_filename
    else:
        # Not a template - return as-is
        return file_content, file_path.name


def execute_script_content(
    script: str,
    mime_type: str,
    env_vars: dict[str, str],
    output_contains: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute script content and return results.

    This is a shared utility function used by both the SDK's example runner
    and the backend's Celery task for consistent execution behavior.

    Args:
        script: The script content to execute (expanded, not a template)
        mime_type: Document MIME type ("python", "javascript", "bash")
        env_vars: Environment variables to set (e.g., {"UNITYSVC_API_KEY": "...", "SERVICE_BASE_URL": "..."})
        output_contains: Optional substring that must appear in stdout for success
        timeout: Execution timeout in seconds (default: 30)

    Returns:
        Result dictionary with:
        - status: "success" | "task_failed" | "script_failed" | "unexpected_output"
        - error: Error message (None if success)
        - exit_code: Script exit code (None if script didn't run)
        - stdout: Standard output (truncated to 1KB)
        - stderr: Standard error (truncated to 1KB)
    """
    import subprocess
    import tempfile

    # Output truncation limit (10KB — must be large enough to capture
    # full Python tracebacks including HTTP error bodies)
    MAX_OUTPUT_SIZE = 10_000

    result: dict[str, Any] = {
        "status": "task_failed",
        "error": None,
        "exit_code": None,
        "stdout": None,
        "stderr": None,
    }

    # Determine interpreter from mime_type
    interpreter_cmd, file_suffix, error = determine_interpreter(script, mime_type)
    if error:
        result["status"] = "task_failed"
        result["error"] = error
        return result

    assert interpreter_cmd is not None, "interpreter_cmd should not be None after error check"

    # Prepare environment
    env = os.environ.copy()
    env.update(env_vars)

    # Write script to temporary file
    temp_file = None
    try:
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=file_suffix,
            delete=False,
        )
        temp_file.write(script)
        temp_file.close()
        os.chmod(temp_file.name, 0o755)

        # Execute script
        process = subprocess.run(
            [interpreter_cmd, temp_file.name],
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        result["exit_code"] = process.returncode
        result["stdout"] = process.stdout[:MAX_OUTPUT_SIZE] if process.stdout else None
        # Keep the tail of stderr — the actual error message is at the bottom
        result["stderr"] = process.stderr[-MAX_OUTPUT_SIZE:] if process.stderr else None

        # Determine status
        if process.returncode != 0:
            result["status"] = "script_failed"
            result["error"] = f"Script exited with code {process.returncode}"
        elif output_contains and (not process.stdout or output_contains.lower() not in process.stdout.lower()):
            result["status"] = "unexpected_output"
            result["error"] = f"Output does not contain: {output_contains}"
        else:
            result["status"] = "success"
            result["error"] = None

    except subprocess.TimeoutExpired:
        result["error"] = f"Script execution timeout ({timeout} seconds)"
    except FileNotFoundError as e:
        result["error"] = f"Interpreter not found: {e}"
    except Exception as e:
        result["error"] = str(e)
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

    return result


def determine_interpreter(script: str, mime_type: str) -> tuple[str | None, str, str | None]:
    """
    Determine the interpreter command for executing a script.

    Checks for shebang line first, then falls back to MIME type-based detection.
    Supported MIME types: "python", "javascript", "bash"

    Args:
        script: The content of the script (used for shebang parsing)
        mime_type: Document MIME type ("python", "javascript", "bash")

    Returns:
        Tuple of (interpreter_cmd, file_suffix, error_message).
        If successful, returns (interpreter_cmd, file_suffix, None).
        If failed, returns (None, "", error_message).

    Examples:
        >>> determine_interpreter("print('hello')", "python")
        ('python3', '.py', None)
        >>> determine_interpreter("console.log('hello')", "javascript")
        ('node', '.js', None)
        >>> determine_interpreter("curl http://example.com", "bash")
        ('bash', '.sh', None)
    """
    import shutil

    # Map MIME type to file suffix
    mime_to_suffix = {
        "python": ".py",
        "javascript": ".js",
        "bash": ".sh",
    }

    file_suffix = mime_to_suffix.get(mime_type, "")
    if not file_suffix:
        return None, "", f"Unsupported MIME type: {mime_type}. Supported: python, javascript, bash"

    # Parse shebang to get interpreter
    lines = script.split("\n")
    interpreter_cmd = None

    # First, try to parse shebang
    if lines and lines[0].startswith("#!"):
        shebang = lines[0][2:].strip()
        if "/env " in shebang:
            # e.g., #!/usr/bin/env python3
            interpreter_cmd = shebang.split("/env ", 1)[1].strip().split()[0]
        else:
            # e.g., #!/usr/bin/python3
            interpreter_cmd = shebang.split("/")[-1].split()[0]

    # If no shebang found, determine interpreter based on MIME type
    if not interpreter_cmd:
        if mime_type == "python":
            # Try python3 first, fallback to python
            if shutil.which("python3"):
                interpreter_cmd = "python3"
            elif shutil.which("python"):
                interpreter_cmd = "python"
            else:
                return None, file_suffix, "Neither 'python3' nor 'python' found."
        elif mime_type == "javascript":
            # JavaScript files need Node.js
            if shutil.which("node"):
                interpreter_cmd = "node"
            else:
                return None, file_suffix, "'node' not found. Please install Node.js."
        elif mime_type == "bash":
            # Shell scripts use bash
            if shutil.which("bash"):
                interpreter_cmd = "bash"
            else:
                return None, file_suffix, "'bash' not found."
    else:
        # Shebang was found - verify the interpreter exists
        if not shutil.which(interpreter_cmd):
            return None, file_suffix, f"Interpreter '{interpreter_cmd}' from shebang not found."

    return interpreter_cmd, file_suffix, None
