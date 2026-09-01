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
**system** template. Read-only ``specs`` commands ignore it because only the
backend can render platform-owned templates; ``specs upload`` sends it to the
backend instantiation endpoint.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from unitysvc_core.utils import deep_merge_dicts

from .template_populate import _deprecate_service, _sanitize_dirname, populate_from_iterator
from .utils import EXPANDED_DIRNAME, load_data_file


class ParamRenderError(ValueError):
    """A param file could not be resolved or rendered (bad template, name clash, …)."""


# The directory the CLI was invoked from, recorded by
# ``materialized_param_specs`` before it chdirs into the ephemeral render copy.
# ``None`` outside that window (concrete repos, non-CLI callers).
_invocation_cwd: Path | None = None


def invocation_cwd() -> Path:
    """Where the user ran the command from — the directory they will look in
    for debugging artifacts.

    While ``materialized_param_specs`` has the process chdir'd into its
    ephemeral copy, ``Path.cwd()`` points at a directory that is deleted when
    the command finishes; anything a user is meant to find afterwards (e.g.
    ``failed_*`` test artifacts) must be written here instead.
    """
    return _invocation_cwd if _invocation_cwd is not None else Path.cwd()


# Filenames that are never param files (they're the spec/aux files themselves).
_RESERVED_STEMS = {"provider", "offering", "listing", "service", "promotion", "service_group", "config"}
# Template-dir files that must NOT be copied verbatim into a rendered folder:
# the two rendered templates and the populator's config.
_NON_BUNDLED = {"offering.json.j2", "listing.json.j2", "config.json"}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def is_param_file(path: Path) -> bool:
    """True if ``path`` looks like a param file: a ``<name>.json`` under ``specs/``
    that is not a reserved spec/aux file and carries a ``parameters`` key.

    ``<name>.override.json`` files are companions to a param file, never param
    files themselves (see :func:`load_param_data`)."""
    if path.suffix != ".json" or path.name.endswith((".service.json", ".override.json")):
        return False
    if path.stem in _RESERVED_STEMS:
        return False
    try:
        data = _load_json(path)
    except Exception:
        return False
    return isinstance(data, dict) and "parameters" in data


def override_file_for(param_file: Path) -> Path:
    """The companion override file: ``specs/<name>.json`` → ``specs/<name>.override.json``."""
    return param_file.with_name(param_file.stem + ".override.json")


def load_param_data(param_file: Path) -> dict[str, Any]:
    """Load a param file, deep-merging its ``<name>.override.json`` companion.

    The override file carries **manual corrections that survive regeneration**:
    a populator script (``update_params.py``) rewrites the base param file on
    every run, while the committed override — same shape as the param file,
    typically just ``{"parameters": {…}}`` — is merged over it at render time
    by every ``specs`` command. Tweak a generated service by writing the
    override; the next populate run can no longer clobber it.

    Dicts merge recursively; scalars and lists in the override replace the
    base value.
    """
    data = _load_json(param_file)
    override = override_file_for(param_file)
    if override.is_file():
        patch = _load_json(override)
        if not isinstance(patch, dict):
            raise ParamRenderError(f"{override}: override file must be a JSON object")
        if not isinstance(data, dict):
            raise ParamRenderError(f"{param_file}: param file must be a JSON object")
        data = deep_merge_dicts(data, patch)
    return data


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
    directory doesn't exist (a non-local template is a system one — upload it
    with ``usvc seller specs upload``).
    """
    templates = _repo_root_for(param_file) / "templates"
    tdir = templates / template_name if template_name else templates
    if not tdir.is_dir():
        ref = template_name or "(default templates/)"
        raise ParamRenderError(
            f"local template '{ref}' not found at {tdir} for {param_file.name}. "
            "System templates are created with `usvc seller specs upload`."
        )
    return tdir


def _resolve_template_dir_or_none(param_file: Path, template_name: str | None) -> Path | None:
    """Return the local template dir for ``param_file``, or ``None`` for a system template."""
    try:
        templates = _repo_root_for(param_file) / "templates"
    except ParamRenderError:
        return None
    tdir = templates / template_name if template_name else templates
    return tdir if tdir.is_dir() else None


def is_local_param_file(param_file: Path) -> bool:
    """True when a param file resolves to a local template directory."""
    data = load_param_data(param_file)
    return _resolve_template_dir_or_none(param_file, data.get("template")) is not None


def discover_local_param_files(root: Path) -> list[Path]:
    """Param files under ``root`` that can be rendered locally."""
    return [p for p in discover_param_files(root) if is_local_param_file(p)]


def discover_system_param_files(root: Path) -> list[Path]:
    """Param files under ``root`` that must be rendered by the backend."""
    return [p for p in discover_param_files(root) if not is_local_param_file(p)]


def _service_name_for(param_file: Path) -> str:
    """Service name = the param file's path under ``specs/``, sans ``.json``."""
    return param_file.relative_to(_specs_root_for(param_file)).with_suffix("").as_posix()


def service_name_for_param(param_file: Path) -> str:
    """Public wrapper for computing the service name represented by a param file."""
    return _service_name_for(param_file)


def _sidecar_for(param_file: Path) -> Path:
    return param_file.with_name(param_file.stem + ".service.json")


def sidecar_for_param(param_file: Path) -> Path:
    """Sidecar path for backend-assigned service metadata of a param file."""
    return _sidecar_for(param_file)


def _read_service_id(sidecar: Path) -> str | None:
    if not sidecar.is_file():
        return None
    try:
        data = json.loads(sidecar.read_text())
    except Exception:
        return None
    sid = data.get("service_id") if isinstance(data, dict) else None
    return str(sid) if sid else None


def read_service_id_for_param(param_file: Path) -> str | None:
    """Read the backend service_id sidecar for ``param_file`` if present."""
    return _read_service_id(_sidecar_for(param_file))


def _read_sidecar_field(sidecar: Path, key: str) -> Any:
    if not sidecar.is_file():
        return None
    try:
        data = json.loads(sidecar.read_text())
    except Exception:
        return None
    return data.get(key) if isinstance(data, dict) else None


def _merge_into_sidecar(sidecar: Path, fields: dict[str, Any]) -> None:
    """Merge *fields* into the committed sidecar, preserving anything already there."""
    data: dict[str, Any] = {}
    if sidecar.is_file():
        try:
            loaded = json.loads(sidecar.read_text())
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}
    data.update(fields)
    sidecar.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _write_service_id(sidecar: Path, service_id: str) -> None:
    _merge_into_sidecar(sidecar, {"service_id": str(service_id)})


def write_service_id_for_param(param_file: Path, service_id: str) -> None:
    """Persist the backend service_id sidecar for ``param_file``."""
    _write_service_id(_sidecar_for(param_file), service_id)


@contextmanager
def materialized_param_specs(root: Path) -> Iterator[list[Path]]:
    """Render every param file into an **isolated temp copy** of the repo and
    ``chdir`` into it for the duration of the ``with`` block, then restore the
    cwd and remove the copy.

    Each ``specs/<provider>/<name>.json`` becomes ``specs/<provider>/<name>/``
    (offering + listing + provider + bundled docs) **inside the copy** — never in
    the real tree. Every ``specs`` command roots its scan at the cwd, so the
    ``chdir`` transparently points the whole pipeline at the copy. This means:

    - concurrent sessions can render / upload / test without colliding on the
      real ``specs/`` (each gets its own temp), and
    - a crashed run can't leave a stale in-place folder that trips the
      "a service is one or the other" guard on the next run.

    On exit the backend-assigned ``service_id`` (and the local
    ``upstream_test_status`` recorded by ``specs run-tests``) written into a
    rendered folder's ``service.json`` is merged back into the committed
    ``<name>.service.json`` sidecar in the **real** repo. Yields the rendered
    folder paths (inside the copy). Use ``specs expand`` for a persistent,
    inspectable render.

    No-op — no copy, no ``chdir`` — when the repo has no param files, so
    concrete-only repos are unaffected.

    System-template param files are left in the temp copy for ``specs upload``
    to send to the backend instantiation endpoint. Other read-only specs
    commands ignore them because they cannot be rendered locally.
    """
    local_param_files = discover_local_param_files(root)
    if not local_param_files:
        # Concrete-only repo: nothing to render, so don't copy or chdir.
        yield []
        return

    repo_root = _repo_root_for(local_param_files[0])  # the dir that holds templates/
    original_cwd = Path.cwd()
    tmp = Path(tempfile.mkdtemp(prefix="usvc-specs-"))
    rendered: list[tuple[Path, Path]] = []  # (folder in copy, REAL sidecar)
    sidecar_pairs: list[tuple[Path, Path]] = []  # (sidecar in copy, REAL sidecar)

    try:
        # A faithful mirror so every template, relative doc ref, and shared file
        # resolves exactly as in the real tree — just in an isolated location.
        shutil.copytree(
            repo_root,
            tmp,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                ".git",
                ".venv",
                "node_modules",
                "__pycache__",
                EXPANDED_DIRNAME,
                "*.out",
                "*.err",
                "*.status",
            ),
        )

        # An override without its base param file is a typo'd filename —
        # fail loud, or the correction it carries silently stops applying.
        for ov in sorted(tmp.rglob("*.override.json")):
            base = ov.with_name(ov.name[: -len(".override.json")] + ".json")
            if not base.is_file():
                rel = ov.relative_to(tmp)
                raise ParamRenderError(
                    f"{rel}: override file has no matching param file ({base.name}) — check the name"
                )

        # Group by resolved template dir so one populate call renders all params
        # that share a template (and so a repo can mix templates).
        groups: dict[Path, list[tuple[Path, dict[str, Any]]]] = {}
        for pf in discover_local_param_files(tmp):
            data = load_param_data(pf)
            tdir = _resolve_template_dir(pf, data.get("template"))
            folder = pf.with_suffix("")
            if folder.exists():
                # A committed param file AND a hand-authored folder for the same
                # service — a genuine authoring conflict (not a stale render).
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
                # Seed service.json from the committed sidecar (copied in) so the
                # upload updates the same service and honours the prior outcome.
                sidecar_in_copy = _sidecar_for(pf)
                seed: dict[str, Any] = {}
                sid = _read_service_id(sidecar_in_copy)
                if sid:
                    seed["service_id"] = sid
                prior = _read_sidecar_field(sidecar_in_copy, "upstream_test_status")
                if prior is not None:
                    seed["upstream_test_status"] = prior
                if seed:
                    (folder / "service.json").write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n")
                # The round-trip on exit must land in the REAL repo's sidecar
                # (same relative path under repo_root), not the throwaway copy.
                real_sidecar = repo_root / sidecar_in_copy.relative_to(tmp)
                rendered.append((folder, real_sidecar))
                sidecar_pairs.append((folder / "service.json", real_sidecar))
                # Drop the param file in the copy so the walk sees exactly one
                # form (the rendered folder) per service.
                pf.unlink()

        for pf in discover_system_param_files(tmp):
            sidecar_in_copy = _sidecar_for(pf)
            real_sidecar = repo_root / sidecar_in_copy.relative_to(tmp)
            sidecar_pairs.append((sidecar_in_copy, real_sidecar))

        # Point the whole cwd-rooted pipeline at the isolated copy, keeping
        # the real invocation dir reachable for user-facing artifact writes.
        global _invocation_cwd
        _invocation_cwd = original_cwd
        os.chdir(tmp)
        yield [folder for folder, _ in rendered]

    finally:
        _invocation_cwd = None
        os.chdir(original_cwd)
        for source_sidecar, real_sidecar in sidecar_pairs:
            # Round-trip the backend-assigned service_id and the local
            # connectivity outcome recorded by `specs run-tests`.
            if source_sidecar.is_file():
                try:
                    rendered_data = json.loads(source_sidecar.read_text())
                except Exception:
                    rendered_data = {}
                if not isinstance(rendered_data, dict):
                    rendered_data = {}
                carry = {k: rendered_data[k] for k in ("service_id", "upstream_test_status") if rendered_data.get(k)}
                if carry:
                    _merge_into_sidecar(real_sidecar, carry)
        shutil.rmtree(tmp, ignore_errors=True)


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
                j2,
                listing=listing,
                offering=offering,
                provider=provider,
                interface=iface,
                local_testing=local_testing,
                **flat_ctx,
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
    data = load_param_data(param_file)
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


class UpstreamEnumerationError(RuntimeError):
    """A provider's model enumeration cannot be trusted to retire anything.

    Raised instead of deprecating, so ``specs populate`` exits non-zero, the
    workflow step fails under ``set -euo pipefail``, and the PR-creation step is
    skipped entirely — a bad enumeration produces a red build and NO pull
    request, rather than one full of wrong deprecations for a human to
    rubber-stamp.
    """


# Companion files that sit beside a param file and are NOT services: the
# backend-assigned identity record, and the per-service override that replaced
# the _FC_DENYLIST. 36 of the latter exist across six repos, so a bare
# ``*.json`` glob would treat each as a service with no upstream match and
# deprecate it.
_NON_SERVICE_SUFFIXES = (".service.json", ".override.json")


def _committed_service_names(root: Path) -> dict[str, Path]:
    """Every service committed under ``root``, by service name.

    Both shapes contribute to one namespace, because the service name IS the
    path: ``<NAME>.json`` (param file) and ``<NAME>/offering.json`` (the
    expanded folder one repo still holds). The value is the param file, or the
    folder for an expanded service.
    """
    folders = _expanded_service_folders(root)
    found: dict[str, Path] = {f.relative_to(root).as_posix(): f for f in folders}
    inside_a_folder = set(folders)

    for f in root.rglob("*.json"):
        if f.name.endswith(_NON_SERVICE_SUFFIXES):
            continue
        if f.parent in inside_a_folder:
            continue  # offering/listing/service/provider.json of an expanded service
        found.setdefault(f.relative_to(root).as_posix()[: -len(".json")], f)
    return found


def preserve_known_values(new: Any, committed: Any, stats: dict[str, int] | None = None) -> Any:
    """Merge ``new`` over ``committed`` so a ``None`` never replaces a value.

    Populate scripts enrich each service from third-party APIs, and by the time
    a value reaches the writer the reason for a ``None`` is gone. The
    HuggingFace lookup, for instance, tries several URL variations and keeps
    only ``status_code == 200``, so a 429, a timeout and a genuine 404 all
    arrive as the same ``None``. One parasail run silently nulled
    ``parameter_count`` on 45 services from values HuggingFace still serves.

    Since "we could not find out" cannot be told from "there is definitively
    nothing", the committed value wins: it is strictly more informative than
    either reading of ``None``. The code that produces these fields already
    says as much — ``null is the sentinel for "unknown"``.

    Only ``None`` is affected. A real new value always overwrites, including a
    falsy one (``0``, ``""``, ``False``), and a key the iterator drops entirely
    still disappears — this rule is about unknown values, not about making
    fields immortal.
    """
    if isinstance(new, dict) and isinstance(committed, dict):
        merged = dict(new)
        for key, value in new.items():
            if key in committed:
                merged[key] = preserve_known_values(value, committed[key], stats)
        return merged
    if new is None and committed is not None:
        if stats is not None:
            stats["preserved"] += 1
        return committed
    return new


def _deprecate_param_file(path: Path) -> bool:
    """Set ``parameters.status = "deprecated"``. False if already deprecated."""
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    params = data.setdefault("parameters", {})
    if params.get("status") == "deprecated":
        return False
    params["status"] = "deprecated"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return True


def _deprecate_missing_services(remaining: dict[str, Path], committed_total: int, stats: dict[str, int]) -> None:
    """Deprecate every committed service the iterator did not account for.

    ``remaining`` starts as everything committed under ``output_dir`` and is
    drained as the iterator yields, so what is left never appeared in this run.

    Guard: if that is *everything*, the run did not fail to find a few retired
    models — it failed. A populator that errored, authenticated wrongly, or hit
    an endpoint returning nobody's models looks exactly like a catalog that
    retired all at once, and only one of those is real. Refuse.

    Nothing needs unwinding when this raises: the workflow's ``git add specs/``
    and PR-creation steps never run once the populate step exits non-zero, so
    a half-written tree is discarded with the runner.
    """
    if committed_total and len(remaining) == committed_total:
        raise UpstreamEnumerationError(
            f"the iterator matched none of the {committed_total} committed "
            "service(s), so every one of them would be deprecated. That is a "
            "failed populate, not a retired catalog — refusing.\n"
            f"  committed sample: {sorted(remaining)[:3]}\n"
            "Check the provider credential and endpoint, and that each yielded "
            "'service_name' is the service's path under specs/ "
            "(e.g. 'nebius/Qwen/Qwen3-32B', not 'Qwen/Qwen3-32B')."
        )

    for name in sorted(remaining):
        target = remaining[name]
        changed = _deprecate_service(target) if target.is_dir() else _deprecate_param_file(target)
        if changed:
            print(f"  deprecated (not served upstream): {name}")
            stats["deprecated"] += 1
        else:
            stats["already_deprecated"] += 1


def write_params_from_iterator(
    iterator: Iterator[dict[str, Any]],
    output_dir: str | Path,
    *,
    template: str | None = None,
    deprecate_missing: bool = True,
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
        iterator: Yields template-variable dicts; each **must** carry
            ``service_name`` — the service's name, which is also its path under
            ``specs/`` (e.g. ``"cohere/command-r"`` →
            ``specs/cohere/command-r.json``). There is no alternate key and no
            fallback: a second way for the same value to arrive is exactly the
            ambiguity this contract removes. The ``parameters`` written are the
            dict minus the path-derived keys
            (``name``/``service_name``/``provider_name``).
        output_dir: The ``specs/`` directory to write param files into.
        template: Optional local-template name recorded in each param file. ``None``
            (default) means the repo's ``templates/`` root renders the params.
        deprecate_missing: Mark every committed service the iterator did NOT
            yield as ``status="deprecated"`` (default True, matching
            ``populate_from_iterator``'s argument of the same name).

            The set of committed services is read from ``output_dir`` before
            the run and drained as each service is yielded, so what remains
            never appeared — the upstream stopped serving it. Nothing external
            has to be passed: a model the script filters out is filtered on
            *every* run, so it was never committed and cannot be in the
            remainder.

            Set False to leave stale entries alone (e.g. a repo whose
            populator covers only part of its catalog).

    Returns:
        Stats dict: ``{"total", "written", "new", "preserved", "errors",
        "deprecated", "already_deprecated"}``. ``preserved`` counts values the
        iterator yielded as ``None`` that were kept from the committed file.

    Raises:
        UpstreamEnumerationError: the iterator matched none of the committed
            services, so all of them would be deprecated — a failed populate,
            not a retired catalog.
        ParamRenderError: a yielded name is not usable verbatim as a path.
    """
    output_dir = Path(output_dir)
    stats = {
        "total": 0,
        "written": 0,
        "new": 0,
        "preserved": 0,
        "errors": 0,
        "deprecated": 0,
        "already_deprecated": 0,
    }

    # Everything committed before this run. Each yielded service is drained out
    # below, so whatever is still here at the end never appeared in this run —
    # i.e. the upstream stopped serving it.
    remaining = _committed_service_names(output_dir)
    committed_total = len(remaining)
    seen: set[str] = set()

    for model_data in iterator:
        stats["total"] += 1
        name = model_data.get("service_name")
        if not name:
            # Hard failure, not a skip. A silently dropped service is a service
            # that vanishes from the catalog on the next upload, and — now that
            # absence drives deprecation — one that could be retired for no
            # reason other than its populator forgetting a key.
            raise ParamRenderError(
                "iterator yielded a service with no 'service_name'. Every "
                "populate script must state it explicitly; it is the service's "
                "identity and its path under specs/. Offending entry: "
                f"{sorted(model_data)[:8]}"
            )

        rel = _sanitize_dirname(name)
        # The service name IS the path, so a name the filesystem cannot hold
        # verbatim would silently split the two apart: a future ``llama3:8b``
        # lands at ``llama3_8b`` and every later name-to-path comparison —
        # deprecation included — quietly misses. Refuse rather than sanitise.
        # This is a no-op on every name in every repo today.
        if rel != name:
            raise ParamRenderError(
                f"service name {name!r} is not usable as a path (it would be "
                f"written as {rel!r}). The service name must equal its location "
                "under specs/; normalise it in the populate script instead."
            )
        seen.add(rel)
        param_path = output_dir / f"{rel}.json"
        param_path.parent.mkdir(parents=True, exist_ok=True)

        parameters = {k: v for k, v in model_data.items() if k not in _PATH_DERIVED_KEYS}

        # A null must not overwrite a value we already have — an enrichment
        # lookup that failed is indistinguishable from one that found nothing.
        # Read the committed param file directly rather than via
        # ``load_param_data``: that merges the ``.override.json`` companion,
        # and absorbing an override's value into the generated file would make
        # the override look redundant and invite its deletion.
        if param_path.is_file():
            try:
                previous = (json.loads(param_path.read_text()) or {}).get("parameters")
            except (json.JSONDecodeError, OSError):
                previous = None
            if isinstance(previous, dict):
                parameters = preserve_known_values(parameters, previous, stats)

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

        # This service is accounted for; drop it from the set of committed
        # services still awaiting an explanation.
        if remaining.pop(rel, None) is None:
            stats["new"] += 1

        stats["written"] += 1
        print(f"  wrote {param_path.relative_to(output_dir)}" + (f"  (service_id {sid[:8]}…)" if sid else ""))

    if deprecate_missing:
        _deprecate_missing_services(remaining, committed_total, stats)

    return stats
