"""Render local *param files* into ephemeral service folders.

A **param file** is a compact way to author a service: ``specs/<provider>/<name>.json``
containing ``{ "template": <name>?, "parameters": {...} }``. At validate / upload
/ run-tests time it is rendered through a **local template directory** into a
self-contained service folder (``specs/<provider>/<name>/``) that the normal
``specs`` pipeline then handles. The generated folder is **ephemeral** — only the
param file and its ``<name>.service.json`` sidecar are committed.

Rendering reuses :func:`unitysvc_sellers.template_populate.populate_from_iterator`
(the same engine the populator uses); this module only adds param-file discovery,
template resolution, bundling of the template's extra files, and the
``service.json`` ↔ sidecar round-trip — wrapped in :func:`materialized_param_specs`,
a context manager the commands enter so the rendered folders exist for the
duration of the walk and are cleaned up afterwards.

A param file whose ``template`` does not resolve to a local directory is a
**remote** template — handled by ``usvc_seller params instantiate``, not here.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import json5

from .template_populate import populate_from_iterator


class ParamRenderError(ValueError):
    """A param file could not be resolved or rendered (bad template, name clash, …)."""


# Filenames that are never param files (they're the spec/aux files themselves).
_RESERVED_STEMS = {"provider", "offering", "listing", "service", "promotion", "service_group", "config"}
# Template-dir files that must NOT be copied verbatim into a rendered folder:
# the two rendered templates and the populator's config.
_NON_BUNDLED = {"offering.json.j2", "listing.json.j2", "config.json"}


def _load_json(path: Path) -> Any:
    return json5.loads(path.read_text())


def is_param_file(path: Path) -> bool:
    """True if ``path`` looks like a param file: a ``<name>.json`` under ``specs/``
    that is not a reserved spec/aux file and carries a ``parameters`` key."""
    if path.suffix != ".json" or path.name.endswith(".service.json"):
        return False
    if path.stem in _RESERVED_STEMS:
        return False
    try:
        data = _load_json(path)
    except Exception:
        return False
    return isinstance(data, dict) and "parameters" in data


def discover_param_files(root: Path) -> list[Path]:
    """All param files under ``root`` (recursively), sorted."""
    return sorted(p for p in root.rglob("*.json") if is_param_file(p))


def _repo_root_for(param_file: Path) -> Path:
    """The nearest ancestor that contains a ``templates/`` directory."""
    for parent in param_file.parents:
        if (parent / "templates").is_dir():
            return parent
    raise ParamRenderError(f"no 'templates/' directory found above param file {param_file}")


def _specs_root_for(param_file: Path) -> Path:
    """The ``specs/`` directory the param file lives under (for path → name)."""
    for parent in param_file.parents:
        if parent.name == "specs":
            return parent
    # Fallback: assume specs/ is a sibling of templates/.
    return _repo_root_for(param_file) / "specs"


def _resolve_template_dir(param_file: Path, template_name: str | None) -> Path:
    """Resolve a param file's ``template`` to a local template directory.

    ``None`` → ``templates/``; ``"resp"`` → ``templates/resp/``. Raises if the
    directory doesn't exist (a non-local template is a remote one — use
    ``params instantiate``).
    """
    templates = _repo_root_for(param_file) / "templates"
    tdir = templates / template_name if template_name else templates
    if not tdir.is_dir():
        ref = template_name or "(default templates/)"
        raise ParamRenderError(
            f"local template '{ref}' not found at {tdir} for {param_file.name}. "
            f"Remote/system templates are created with `usvc_seller params instantiate`."
        )
    return tdir


def _service_name_for(param_file: Path) -> str:
    """Service name = the param file's path under ``specs/``, sans ``.json``."""
    return param_file.relative_to(_specs_root_for(param_file)).with_suffix("").as_posix()


def _sidecar_for(param_file: Path) -> Path:
    return param_file.with_name(param_file.stem + ".service.json")


def _read_service_id(sidecar: Path) -> str | None:
    if not sidecar.is_file():
        return None
    try:
        data = json.loads(sidecar.read_text())
    except Exception:
        return None
    sid = data.get("service_id") if isinstance(data, dict) else None
    return str(sid) if sid else None


def _write_service_id(sidecar: Path, service_id: str) -> None:
    data: dict[str, Any] = {}
    if sidecar.is_file():
        try:
            loaded = json.loads(sidecar.read_text())
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}
    data["service_id"] = str(service_id)
    sidecar.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


@contextmanager
def materialized_param_specs(root: Path) -> Iterator[list[Path]]:
    """Render every param file under ``root`` into a sibling service folder for
    the duration of the ``with`` block, then clean up.

    Each ``specs/<provider>/<name>.json`` becomes ``specs/<provider>/<name>/``
    (offering + listing + provider + bundled docs). On exit the
    backend-assigned ``service_id`` written into the folder's ``service.json`` is
    copied back to the committed ``<name>.service.json`` sidecar, and the folder
    is removed. Yields the list of rendered folders.

    Local templates only: a param file whose ``template`` is not a local dir
    raises (it belongs to ``params instantiate``).
    """
    param_files = discover_param_files(root)
    rendered: list[tuple[Path, Path]] = []  # (folder, sidecar)

    try:
        # Group by resolved template dir so one populate call renders all params
        # that share a template (and so a repo can mix templates).
        groups: dict[Path, list[tuple[Path, dict[str, Any]]]] = {}
        for pf in param_files:
            data = _load_json(pf)
            tdir = _resolve_template_dir(pf, data.get("template"))
            folder = pf.with_suffix("")
            if folder.exists():
                raise ParamRenderError(
                    f"both {pf.name} and folder {folder.name}/ exist for service "
                    f"'{_service_name_for(pf)}' — a service is one or the other."
                )
            service_name = _service_name_for(pf)
            ctx: dict[str, Any] = {
                "name": service_name,  # name_field → folder path under output_dir
                "service_name": service_name,
            }
            # provider_name only applies to a namespaced (provider/service)
            # name; a top-level service (a bare name like ``resp200``) has no
            # provider segment, so it's omitted rather than set to the whole
            # name. Templates for top-level services hardcode their provider.
            if "/" in service_name:
                ctx["provider_name"] = service_name.split("/")[0]
            ctx.update(data.get("parameters") or {})
            groups.setdefault(tdir, []).append((pf, ctx))

        for tdir, items in groups.items():
            specs_root = _specs_root_for(items[0][0])
            # Reuse the populator's render engine; silence its progress output
            # (this is an internal expansion, not a user-facing populate).
            with contextlib.redirect_stdout(io.StringIO()):
                populate_from_iterator(
                    iter([ctx for _pf, ctx in items]),
                    templates_dir=tdir,
                    output_dir=specs_root,
                    deprecate_missing=False,
                )
            extras = [f for f in tdir.iterdir() if f.is_file() and f.name not in (_NON_BUNDLED | {"provider.json"})]
            for pf, ctx in items:
                folder = specs_root / ctx["name"]
                # Bundle the template's other files (e.g. connectivity.sh.j2)
                # so the folder is self-contained (provider.json already copied).
                for f in extras:
                    shutil.copyfile(f, folder / f.name)
                # Seed service.json from the committed sidecar so the upload
                # updates the same service.
                sidecar = _sidecar_for(pf)
                sid = _read_service_id(sidecar)
                if sid:
                    (folder / "service.json").write_text(
                        json.dumps({"service_id": sid}, indent=2, sort_keys=True) + "\n"
                    )
                rendered.append((folder, sidecar))

        yield [folder for folder, _ in rendered]

    finally:
        for folder, sidecar in rendered:
            # Round-trip any backend-assigned service_id back to the sidecar.
            service_json = folder / "service.json"
            if service_json.is_file():
                try:
                    sid = json.loads(service_json.read_text()).get("service_id")
                except Exception:
                    sid = None
                if sid:
                    _write_service_id(sidecar, str(sid))
            shutil.rmtree(folder, ignore_errors=True)
