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
import re
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import json5

from .template_populate import _sanitize_dirname, populate_from_iterator
from .utils import EXPANDED_DIRNAME, load_data_file


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
            ctx = {
                "name": service_name,  # name_field → folder path under output_dir
                "service_name": service_name,
                "provider_name": service_name.split("/")[0],
                **(data.get("parameters") or {}),
            }
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


def _localize_file_paths(obj: Any, folder: Path) -> bool:
    """Copy any absolute ``file_path`` in *obj* into *folder* and rewrite it to the
    local basename. Returns True if anything was localized.

    Preset expansion (``$doc_preset`` / ``$file_preset``) yields records whose
    ``file_path`` is an absolute path into the installed ``unitysvc-data``
    package; copying the file in beside the JSON makes the rendered folder
    self-contained for inspection.
    """
    changed = False
    if isinstance(obj, dict):
        fp = obj.get("file_path")
        if isinstance(fp, str) and Path(fp).is_absolute() and Path(fp).is_file():
            shutil.copyfile(fp, folder / Path(fp).name)
            obj["file_path"] = Path(fp).name
            changed = True
        for value in obj.values():
            changed = _localize_file_paths(value, folder) or changed
    elif isinstance(obj, list):
        for value in obj:
            changed = _localize_file_paths(value, folder) or changed
    return changed


def _localize_relative_file_paths(obj: Any, folder: Path, source_base: Path, claimed: dict[str, Path]) -> bool:
    """Copy any *relative* ``file_path`` (resolved against *source_base*) into
    *folder* and rewrite it to the local basename. Returns True if a reference was
    rewritten. ``claimed`` maps basename → source so same-basename clashes are
    reported (last-wins). Absolute paths and ``$preset`` sentinels are left alone
    (handled by :func:`_materialize_presets`)."""
    changed = False
    if isinstance(obj, dict):
        fp = obj.get("file_path")
        if isinstance(fp, str) and fp and not Path(fp).is_absolute():
            src = source_base / fp
            if src.is_file():
                prior = claimed.get(src.name)
                if prior is not None and prior != src:
                    print(f"  ⚠ expand: two docs both map to '{src.name}' ({prior} vs {src}); keeping the latter")
                claimed[src.name] = src
                shutil.copyfile(src, folder / src.name)
                if fp != src.name:
                    obj["file_path"] = src.name
                    changed = True
        for value in obj.values():
            changed = _localize_relative_file_paths(value, folder, source_base, claimed) or changed
    elif isinstance(obj, list):
        for value in obj:
            changed = _localize_relative_file_paths(value, folder, source_base, claimed) or changed
    return changed


def _inline_local_docs(folder: Path, source_base: Path) -> None:
    """Pull every doc a spec references by *relative path* (e.g. a shared
    ``../../docs/connectivity.sh.j2``) into *folder*, rewriting the reference to
    the local basename — so the expanded folder is self-contained for files that
    exist locally, regardless of where they were authored. Resolves relative
    paths against *source_base* (the service's real/canonical location)."""
    claimed: dict[str, Path] = {}
    for kind in ("provider", "offering", "listing"):
        path = folder / f"{kind}.json"
        if not path.is_file():
            continue
        data = _load_json(path)
        if not isinstance(data, dict):
            continue
        if _localize_relative_file_paths(data, folder, source_base, claimed):
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def _materialize_presets(folder: Path) -> None:
    """Resolve ``$doc_preset`` / ``$file_preset`` references in a rendered folder.

    For each spec file, expand its preset sentinels (via the preset-aware
    :func:`load_data_file`), copy any referenced document files in beside the
    JSON, and write the resolved form back — but only when expansion actually
    changed the file, so preset-free specs stay byte-for-byte as rendered.
    """
    for kind in ("provider", "offering", "listing"):
        path = folder / f"{kind}.json"
        if not path.is_file():
            continue
        try:
            expanded, _ = load_data_file(path)
        except Exception as exc:  # unknown preset, bad sentinel, … — best-effort: warn and keep the sentinel
            print(f"  ⚠ expand: could not resolve presets in {kind}.json — left as-authored ({exc})")
            continue
        if not isinstance(expanded, dict):
            continue
        _localize_file_paths(expanded, folder)
        if expanded != _load_json(path):
            path.write_text(json.dumps(expanded, indent=2, ensure_ascii=False) + "\n")


def _variant_name(filename: str, mode: str) -> str:
    """``connectivity.sh`` + ``local`` → ``connectivity.local.sh`` (mode before ext)."""
    if "." in filename:
        base, ext = filename.rsplit(".", 1)
        return f"{base}.{mode}.{ext}"
    return f"{filename}.{mode}"


def _first_interface(config: Any) -> dict[str, Any]:
    """The first channel dict of an ``{upstream,user}_access_config`` mapping."""
    if isinstance(config, dict):
        return next((v for v in config.values() if isinstance(v, dict)), {})
    return {}


# ``${ secrets.VAR }`` / ``${ customer_secrets.VAR ?? default }`` anywhere in a string
# (the in-string form; mirrors example.py's whole-string ``_SECRETS_RE``).
_SECRET_REF_RE = re.compile(r"\$\{\s*(?:secrets|customer_secrets)\.([A-Za-z_]\w*)(?:\s*\?\?\s*(.*?))?\s*\}")


def _localize_secret_refs(text: str) -> str:
    """Rewrite secret references to env-var form for the **local** test variant.

    ``data run-tests`` pulls every ``${ secrets.X }`` / ``${ customer_secrets.X }``
    from an environment variable named ``X`` (see ``example.resolve_secret_ref``),
    so the local script should read the env var, not the catalog reference:
    ``${ ns.X }`` → ``${X}`` and ``${ ns.X ?? default }`` → ``${X:-default}`` (shell
    default-expansion, preserving the fallback). The **gateway** variant keeps the
    references — the gateway resolves customer secrets server-side.
    """

    def repl(m: re.Match[str]) -> str:
        name, default = m.group(1), m.group(2)
        return f"${{{name}:-{default}}}" if default is not None else f"${{{name}}}"

    return _SECRET_REF_RE.sub(repl, text)


def _render_test_variants(folder: Path) -> None:
    """Render every ``.j2`` in *folder* in both test modes — always writing
    ``<base>.local.<ext>`` and ``<base>.gateway.<ext>`` beside the kept template.

    The two modes differ by **interface**, mirroring the backend: the local
    variant (``data run-tests``) renders against the offering's *upstream*
    interface, so ``{{ service_base_url }}`` is the upstream URL; the gateway
    variant (``services run-tests``) renders against the listing's
    *user_access_interface*, so ``{{ service_base_url }}`` is the gateway URL
    (``${API_GATEWAY_BASE_URL}/<service_name>`` — with ``{{ service_name }}``
    resolved and the deployment base left as a ``${...}`` placeholder). Shell
    ``${SERVICE_BASE_URL}`` / ``${customer_secrets.*}`` and unresolved tokens stay
    as placeholders — what the live runner fills in.
    """
    from .example import build_upstream_template_context
    from .utils import render_template_file

    def _load(name: str) -> dict[str, Any]:
        path = folder / name
        if not path.is_file():
            return {}
        try:
            loaded, _ = load_data_file(path)
        except Exception:
            loaded = _load_json(path)  # best-effort: an unresolved preset doesn't block test rendering
        return loaded if isinstance(loaded, dict) else {}

    listing, offering, provider = _load("listing.json"), _load("offering.json"), _load("provider.json")
    service_name = (listing.get("name") or offering.get("name") or "") if isinstance(listing, dict) else ""

    # Local = offering upstream interface; gateway = listing user_access_interface
    # with {{ service_name }} resolved (the deployment base stays a placeholder).
    upstream_iface = _first_interface(offering.get("upstream_access_config") if isinstance(offering, dict) else None)
    gateway_iface = dict(_first_interface(listing.get("user_access_interfaces") if isinstance(listing, dict) else None))
    if isinstance(gateway_iface.get("base_url"), str):
        gateway_iface["base_url"] = re.sub(r"{{\s*service_name\s*}}", service_name, gateway_iface["base_url"])

    modes = {
        "local": (True, upstream_iface, build_upstream_template_context(upstream_iface)),
        "gateway": (False, gateway_iface, build_upstream_template_context(gateway_iface)),
    }
    for j2 in sorted(folder.glob("*.j2")):
        for mode, (local_testing, iface, flat_ctx) in modes.items():
            content, rendered_name = render_template_file(
                j2, listing=listing, offering=offering, provider=provider,
                interface=iface, local_testing=local_testing, **flat_ctx,
            )
            if mode == "local":
                # Local run-tests reads secrets from env vars; don't leak ${ customer_secrets.X }.
                content = _localize_secret_refs(content)
            (folder / _variant_name(rendered_name, mode)).write_text(content)


def _postprocess(leaf: Path, *, source_base: Path) -> None:
    """Fully resolve an expanded folder for inspection: inline locally-referenced
    shared docs, resolve presets (best-effort — a broken preset warns and is left
    as-authored, never fails), and render test variants. Order matters: resolve
    every doc to a local ``.j2`` *before* rendering test variants from those files.
    """
    _inline_local_docs(leaf, source_base)
    _materialize_presets(leaf)
    _render_test_variants(leaf)


def _render_one(ctx: dict[str, Any], tdir: Path, into_root: Path, *, source_base: Path) -> Path:
    """Render ``ctx`` into ``into_root/<ctx['name']>/`` and return that leaf folder:
    populate the templates, bundle the template's extra files, then post-process.
    Shared by the nested and ``--flat`` expand paths.
    """
    with contextlib.redirect_stdout(io.StringIO()):
        populate_from_iterator(iter([ctx]), templates_dir=tdir, output_dir=into_root, deprecate_missing=False)
    leaf = into_root / ctx["name"]
    # Bundle the template's other files (e.g. connectivity.sh.j2) so the folder
    # is self-contained (provider.json is already copied by the populator).
    extras = [f for f in tdir.iterdir() if f.is_file() and f.name not in (_NON_BUNDLED | {"provider.json"})]
    for f in extras:
        shutil.copyfile(f, leaf / f.name)
    _postprocess(leaf, source_base=source_base)
    return leaf


def expand_param_file(
    param_file: Path,
    *,
    output_dir: Path | None = None,
    flat: bool = False,
) -> Path:
    """Render one param file into the informal ``expanded/`` inspection tree.

    ``specs/<name>.json`` → ``expanded/<name>/`` (provider + offering + listing +
    bundled template files), beside ``specs/`` at the repo root. Unlike the
    ephemeral render in :func:`materialized_param_specs`, this folder is a
    **static, user-owned artifact**: it is refreshed in place on each call and
    then left on disk for inspection. It never carries a ``service.json`` —
    backend identity stays with the param file's ``<name>.service.json`` sidecar
    — and every formal command ignores the default ``expanded/`` tree (see
    :data:`unitysvc_sellers.utils.EXPANDED_DIRNAME`), so a stale render (e.g.
    after a template change) is harmless until the next ``expand``.

    Expand resolves everything by default: it inlines docs referenced by a
    **relative path** (e.g. a shared ``../../docs/connectivity.sh.j2``), resolves
    ``$doc_preset`` / ``$file_preset`` references (best-effort — a broken preset
    warns and is left as-authored, never fails), and renders every ``.j2`` in
    local- and gateway-test modes.

    ``output_dir`` overrides the default ``expanded/`` location. By default the
    full ``<service_name>`` path is created beneath it, so expanding several
    services into one directory never collides. With ``flat``, the spec files are
    written **directly** into the directory (no ``<service_name>/``) for
    predictable paths — which only holds one service at a time, so it overwrites
    its own spec files but leaves any other files in the directory untouched.

    Returns the rendered folder path (the ``<service_name>/`` leaf, or the
    directory itself when ``flat``).
    """
    data = _load_json(param_file)
    tdir = _resolve_template_dir(param_file, data.get("template"))
    specs_root = _specs_root_for(param_file)
    service_name = _service_name_for(param_file)
    expanded_root = Path(output_dir) if output_dir is not None else specs_root.parent / EXPANDED_DIRNAME

    ctx = {
        "name": service_name,  # name_field → folder path under output_dir
        "service_name": service_name,
        "provider_name": service_name.split("/")[0],
        **(data.get("parameters") or {}),
    }
    # Relative doc refs resolve against where the service *would* live in specs/
    # (its canonical location), matching how the upload pipeline renders them.
    source_base = specs_root / service_name

    if flat:
        # Render into a throwaway tree, then copy just this service's files in —
        # so a shared output dir keeps its other contents (can't blanket-rmtree).
        with tempfile.TemporaryDirectory() as tmp:
            leaf = _render_one(ctx, tdir, Path(tmp), source_base=source_base)
            expanded_root.mkdir(parents=True, exist_ok=True)
            for f in leaf.iterdir():
                if f.is_file():
                    shutil.copyfile(f, expanded_root / f.name)
        return expanded_root

    folder = expanded_root / service_name
    # Refresh in place: drop any previous render so a removed/renamed file in the
    # template doesn't linger.
    if folder.exists():
        shutil.rmtree(folder)
    _render_one(ctx, tdir, expanded_root, source_base=source_base)
    return folder


def expand_service_folder(
    service_dir: Path,
    *,
    output_dir: Path | None = None,
    flat: bool = False,
) -> Path:
    """Expand a hand-authored ``specs/<name>/`` service folder for inspection.

    Unlike :func:`expand_param_file` there's no template to render — the
    provider/offering/listing already exist — so this copies the folder into the
    informal ``expanded/`` tree and applies the same post-processing as
    :func:`expand_param_file` (inline shared docs, resolve presets best-effort,
    render test variants). The ``service.json`` identity record is never copied.
    ``output_dir`` / ``flat`` behave as there. Returns the expanded folder path.
    """
    specs_root = _specs_root_for(service_dir)
    service_name = service_dir.relative_to(specs_root).as_posix()
    expanded_root = Path(output_dir) if output_dir is not None else specs_root.parent / EXPANDED_DIRNAME
    folder = expanded_root if flat else expanded_root / service_name

    # Non-flat: clean refresh of this service's folder. Flat: merge into the dir
    # without disturbing files that belong to other services / the user.
    if not flat and folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for item in service_dir.iterdir():
        if item.name == "service.json":  # identity stays in the formal tree, never the inspection copy
            continue
        if item.is_dir():
            shutil.copytree(item, folder / item.name, dirs_exist_ok=True)
        else:
            shutil.copyfile(item, folder / item.name)

    # Relative doc refs resolve against the service's real directory.
    _postprocess(folder, source_base=service_dir)
    return folder


# Keys that ``materialized_param_specs`` injects from the param file's path, so
# they must NOT be baked into the param file's ``parameters`` (they'd shadow the
# path-derived values and drift if the file is ever moved/renamed).
_PATH_DERIVED_KEYS = ("name", "service_name", "provider_name")


def _expanded_service_folders(root: Path) -> list[Path]:
    """Every expanded service folder under ``root`` (a dir holding offering.json
    or service.json), keyed deepest-first so nested ones remove cleanly."""
    seen: dict[Path, None] = {}
    for marker in ("offering.json", "service.json"):
        for f in root.rglob(marker):
            seen[f.parent] = None
    return sorted(seen, key=lambda p: len(p.parts), reverse=True)


def write_params_from_iterator(
    iterator: Iterator[dict[str, Any]],
    output_dir: str | Path,
    *,
    template: str | None = None,
    name_field: str = "name",
    prune_missing: bool = False,
) -> dict[str, int]:
    """Write one **param file** per yielded var-dict (the params mirror of
    :func:`populate_from_iterator`).

    Where ``populate_from_iterator`` renders each model dict into an expanded
    ``<name>/`` service folder, this writes the *inputs* instead: a compact
    ``output_dir/<name>.json`` = ``{template?, parameters}`` that the ``specs``
    pipeline re-renders ephemerally at validate / upload / run-tests time (see
    :func:`materialized_param_specs`). The expanded folder for each rendered
    service is removed, so a repo flips from "committed renders" to "committed
    inputs" in one pass.

    Identity is preserved: a ``service_id`` found in the soon-to-be-removed
    ``<name>/service.json`` (or an existing ``<name>.service.json`` sidecar) is
    written to the committed ``<name>.service.json`` sidecar.

    Args:
        iterator: Yields template-variable dicts; each must carry ``name_field``
            (e.g. ``"cohere/command-r"``). The ``parameters`` written are the dict
            minus the path-derived keys (``name``/``service_name``/``provider_name``).
        output_dir: The ``specs/`` directory to write param files into.
        template: Optional local-template name recorded in each param file. ``None``
            (default) means the repo's ``templates/`` root renders the params.
        name_field: Dict key holding the service name / path (default ``"name"``).
        prune_missing: How to treat expanded service folders the iterator did NOT
            yield (committed locally but not in the live source — e.g. a curated
            off-API model). Default False mirrors ``populate_from_iterator``'s
            non-destructive intent: the folder is **kept** (and logged) so its
            ``service_id`` is never lost. Set True to delete them instead.

    Returns:
        Stats dict: ``{"total", "written", "errors", "pruned", "kept"}``.
    """
    output_dir = Path(output_dir)
    stats = {"total": 0, "written": 0, "errors": 0, "pruned": 0, "kept": 0}
    seen: set[str] = set()

    for model_data in iterator:
        stats["total"] += 1
        name = model_data.get(name_field)
        if not name:
            print(f"  Warning: missing '{name_field}' field, skipping")
            stats["errors"] += 1
            continue

        rel = _sanitize_dirname(name)
        seen.add(rel)
        param_path = output_dir / f"{rel}.json"
        param_path.parent.mkdir(parents=True, exist_ok=True)

        parameters = {k: v for k, v in model_data.items() if k not in _PATH_DERIVED_KEYS}
        payload: dict[str, Any] = {}
        if template is not None:
            payload["template"] = template
        payload["parameters"] = parameters
        param_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

        # Preserve identity: prefer an existing sidecar, else lift the id out of
        # the expanded folder we're about to delete.
        sidecar = output_dir / f"{rel}.service.json"
        sid = _read_service_id(sidecar) or _read_service_id(output_dir / rel / "service.json")
        if sid:
            _write_service_id(sidecar, sid)

        # Replace the expanded render with the param file.
        old_folder = output_dir / rel
        if old_folder.is_dir():
            shutil.rmtree(old_folder, ignore_errors=True)

        stats["written"] += 1
        print(f"  wrote {param_path.relative_to(output_dir)}" + (f"  (service_id {sid[:8]}…)" if sid else ""))

    for folder in _expanded_service_folders(output_dir):
        rel = folder.relative_to(output_dir).as_posix()
        if rel in seen:
            continue
        if prune_missing:
            print(f"  pruned (no live match): {rel}/")
            shutil.rmtree(folder, ignore_errors=True)
            stats["pruned"] += 1
        else:
            print(f"  kept (curated; not in live source): {rel}/")
            stats["kept"] += 1

    return stats
