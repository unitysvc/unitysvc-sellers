"""Platform services a seller publishes (unitysvc/unitysvc#2569).

A platform service is a seller's product: it buys capacity from member
sellers and resells it at a ``/p`` address. It is published together with its
member template — what other sellers instantiate to join it — so the template
is owned through the platform service::

    platform-services/<provider>/<name>/
        provider.json  offering.json  listing.json   # the platform service
        <name>.service.json                           # its service_id (optional)
        member-template/
            template.json  *.json.j2                  # the member template
            template_id.json                          # its id (optional)

Both ids are optional: without ``<name>.service.json`` the backend matches the
seller's platform service by name, and without ``template_id.json`` the
template by ``(name, version)``. After an upload both sidecars are written
back. The member template's name is the folder name (``<name>``).

These folders are never uploaded as ordinary services: ordinary discovery
skips ``platform-services/`` and :func:`upload_directory` sends each folder to
``POST /seller/platform-services``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from unitysvc_core.utils import expand_presets

from .utils import PLATFORM_SERVICES_DIRNAME, dump_canonical_json, is_hidden_path, load_data_file

#: The member template's sub-folder in a platform service folder.
MEMBER_TEMPLATE_DIRNAME = "member-template"

# template.json key -> (request body key, default file name); same convention
# as ``usvc_admin templates upload``.
_BODY_FILES = {
    "provider_template_file": ("provider_template", "provider.json.j2"),
    "offering_template_file": ("offering_template", "offering.json.j2"),
    "listing_template_file": ("listing_template", "listing.json.j2"),
}

_DATA_SUFFIXES = (".json", ".toml")


def find_platform_service_folders(root: Path) -> list[Path]:
    """Every ``platform-services/<provider>/<name>/`` folder under ``root``.

    A folder qualifies when it holds a ``listing.{json,toml}`` directly under
    a ``platform-services`` directory two levels up.
    """
    root = Path(root)
    folders: set[Path] = set()
    for suffix in _DATA_SUFFIXES:
        for listing in root.rglob(f"listing{suffix}"):
            if is_hidden_path(listing, root):
                continue
            folder = listing.parent
            if folder.parent.parent.name == PLATFORM_SERVICES_DIRNAME:
                folders.add(folder)
    return sorted(folders)


def platform_service_sidecar(folder: Path) -> Path:
    """``<folder>/<name>.service.json`` — the platform service's id sidecar."""
    return folder / f"{folder.name}.service.json"


def read_platform_service_id(folder: Path) -> str | None:
    """The platform service's ``service_id`` from its sidecar, if recorded."""
    sidecar = platform_service_sidecar(folder)
    if not sidecar.is_file():
        return None
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"{sidecar}: not readable as JSON -- {exc}") from exc
    service_id = data.get("service_id") if isinstance(data, dict) else None
    return str(service_id) if service_id else None


def write_platform_service_id(folder: Path, service_id: str) -> None:
    """Record ``service_id`` in ``<name>.service.json`` (other keys kept)."""
    sidecar = platform_service_sidecar(folder)
    data: dict[str, Any] = {}
    if sidecar.is_file():
        try:
            loaded = json.loads(sidecar.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except ValueError:
            data = {}
    if data.get("service_id") == service_id:
        return
    data["service_id"] = service_id
    sidecar.write_text(dump_canonical_json(data), encoding="utf-8")


def _inline_file_paths(node: Any) -> None:
    """Replace preset-generated absolute file paths with portable content."""
    if isinstance(node, dict):
        file_path = node.get("file_path")
        if isinstance(file_path, str):
            path = Path(file_path)
            if path.is_absolute() and path.is_file():
                node["file_content"] = path.read_text(encoding="utf-8")
                node["file_path"] = path.name
        for value in node.values():
            _inline_file_paths(value)
    elif isinstance(node, list):
        for item in node:
            _inline_file_paths(item)


def load_member_template(folder: Path) -> dict[str, Any]:
    """The member template of a platform service folder, as an upload body.

    Reads ``member-template/template.json``, names the template after the
    platform service folder (a declared ``name`` must match), carries the
    ``template_id.json`` id when present, inlines the three ``.j2`` bodies and
    expands ``$preset`` sentinels in the metadata.
    """
    template_dir = folder / MEMBER_TEMPLATE_DIRNAME
    meta_path = template_dir / "template.json"
    if not meta_path.is_file():
        raise ValueError(f"{folder}: missing {MEMBER_TEMPLATE_DIRNAME}/template.json")
    data: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
    for legacy in ("schema", "schema_version", "time_created"):
        data.pop(legacy, None)

    declared = data.get("name")
    if declared is None:
        data["name"] = folder.name
    elif declared != folder.name:
        raise ValueError(f"{meta_path}: name {declared!r} does not match the platform service folder {folder.name!r}")

    sidecar = template_dir / "template_id.json"
    if sidecar.is_file():
        recorded = json.loads(sidecar.read_text(encoding="utf-8"))
        template_id = recorded.get("id") if isinstance(recorded, dict) else None
        if template_id:
            data["id"] = template_id

    for file_key, (body_key, default_name) in _BODY_FILES.items():
        file_name = data.pop(file_key, default_name)
        body_path = template_dir / file_name
        if not body_path.is_file():
            raise ValueError(f"{template_dir}: missing {file_name} ({body_key})")
        data[body_key] = body_path.read_text(encoding="utf-8")

    expanded: dict[str, Any] = expand_presets(data)
    _inline_file_paths(expanded)
    return expanded


def write_member_template_id(folder: Path, template_id: str) -> None:
    """Record the member template's id in ``member-template/template_id.json``."""
    sidecar = folder / MEMBER_TEMPLATE_DIRNAME / "template_id.json"
    record = {"id": template_id, "name": folder.name}
    if sidecar.is_file():
        try:
            if json.loads(sidecar.read_text(encoding="utf-8")) == record:
                return
        except ValueError:
            pass
    sidecar.write_text(dump_canonical_json(record), encoding="utf-8")


def build_platform_service_payload(folder: Path, *, client: Any | None = None) -> dict[str, Any]:
    """The ``POST /seller/platform-services`` body for one platform service folder.

    The platform service's own files go through the same loader as an ordinary
    service (presets, convenience fields, file references); the member template
    is loaded by :func:`load_member_template`.
    """
    from .upload import _build_service_payload

    listing_file = next(
        (folder / f"listing{suffix}" for suffix in _DATA_SUFFIXES if (folder / f"listing{suffix}").is_file()),
        None,
    )
    if listing_file is None:
        raise ValueError(f"{folder}: missing listing.json")
    provider_data, offering_data, listing_data, _ = _build_service_payload(listing_file, client=client)
    payload: dict[str, Any] = {
        "service_data": {
            "provider_data": provider_data,
            "offering_data": offering_data,
            "listing_data": listing_data,
        },
        "member_template": load_member_template(folder),
    }
    service_id = read_platform_service_id(folder)
    if service_id:
        payload["service_status"] = {"service_id": service_id}
    return payload


_P_BASE_URL_RE = re.compile(r"^\$\{API_GATEWAY_BASE_URL\}/p/(?P<route>[a-z0-9][a-z0-9_-]*)$")


def validate_platform_service_folder(folder: Path, root: Path) -> list[str]:
    """Offline checks of one ``platform-services/<provider>/<name>/`` folder.

    The checks the platform makes at publish time that need no server: the
    three files parse as their core models, the folder path matches the
    provider and the service name, every listing interface is a ``/p``
    address on one route, and the member template loads (named after the
    folder, its bodies present). Not checked here: the template language,
    ownership and address conflicts — the platform refuses those at upload.
    """
    from pydantic import ValidationError
    from unitysvc_core.models import ProviderData, ServiceListingData, ServiceOfferingData

    try:
        rel = folder.relative_to(root).as_posix()
    except ValueError:
        rel = folder.as_posix()
    errors: list[str] = []
    data: dict[str, dict[str, Any]] = {}
    for kind, model in (
        ("provider", ProviderData),
        ("offering", ServiceOfferingData),
        ("listing", ServiceListingData),
    ):
        path = next((folder / f"{kind}{s}" for s in _DATA_SUFFIXES if (folder / f"{kind}{s}").is_file()), None)
        if path is None:
            errors.append(f"{rel}: missing required {kind} file ({kind}.json or {kind}.toml)")
            continue
        try:
            loaded, _ = load_data_file(path)
            model(**loaded)
            data[kind] = loaded
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(p) for p in err["loc"])
                errors.append(f"{rel}/{path.name}: {loc}: {err['msg']}")
        except Exception as exc:  # noqa: BLE001 — surface, don't crash the run
            errors.append(f"{rel}/{path.name}: {exc}")

    provider_name = folder.parent.name
    expected_name = f"{provider_name}/{folder.name}"
    if "provider" in data and data["provider"].get("name") != provider_name:
        errors.append(f"{rel}/provider.json: name must be {provider_name!r} (the folder's provider)")
    for kind in ("offering", "listing"):
        if kind in data and data[kind].get("name") != expected_name:
            errors.append(f"{rel}/{kind}.json: name must be {expected_name!r} (the folder path)")

    if "listing" in data:
        interfaces = data["listing"].get("user_access_interfaces") or {}
        routes = set()
        if not isinstance(interfaces, dict) or not interfaces:
            errors.append(f"{rel}/listing.json: user_access_interfaces must declare the /p address")
        else:
            for iname, iface in interfaces.items():
                base_url = iface.get("base_url") if isinstance(iface, dict) else None
                match = _P_BASE_URL_RE.match(base_url) if isinstance(base_url, str) else None
                if match is None:
                    errors.append(
                        f"{rel}/listing.json: user_access_interfaces.{iname}.base_url must be "
                        "exactly '${API_GATEWAY_BASE_URL}/p/<route>'"
                    )
                else:
                    routes.add(match.group("route"))
            if len(routes) > 1:
                errors.append(f"{rel}/listing.json: all user_access_interfaces must share one /p route")

    try:
        template = load_member_template(folder)
        for key in ("version", "display_name", "service_type"):
            if not template.get(key):
                errors.append(f"{rel}/{MEMBER_TEMPLATE_DIRNAME}/template.json: missing {key!r}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{rel}: {exc}")
    return errors
