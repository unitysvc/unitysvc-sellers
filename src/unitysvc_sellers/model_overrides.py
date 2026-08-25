"""Repo-committed corrections to fetched model metadata.

Populator scripts in ``unitysvc-services-*`` repos build their catalogs from a
provider's live model API plus registries like LiteLLM — sources that are
sometimes wrong about individual models (a model listed but dead at inference,
a "supports tools" flag the actual deployment rejects, a subscription tier the
seller doesn't have). Until now each repo corrected these with ad-hoc in-code
denylists (``_FC_DENYLIST``, ``_DEAD_MODELS``), which require a Python edit per
correction and don't survive hand-flipped param values being regenerated.

This module defines the shared convention that replaces them: a repo-committed
``services/model_overrides.toml`` the populator re-applies on every run, so
human observations of upstream reality always win over fetched metadata.

File format::

    # services/model_overrides.toml
    [models."greg-1-mini"]
    skip = true
    comment = "Listed in /v2/models but inference 404s 'Model Not Known' (2026-08-25)"

    [models."mistral-large-2512"]
    deprecated = true
    comment = "Not in our subscription tier"

    [models."Qwen/Qwen2.5-VL-72B-Instruct"]
    supports_tools = false
    comment = "LiteLLM says true; deployment 400s on tools"

Reserved keys per model entry:

- ``skip`` (bool) — exclude the model from the fetched list entirely: never
  (re)created, and not counted "active" (so an existing catalog entry flows
  into the repo's deprecation/prune pass). Requires ``comment``.
- ``deprecated`` (bool) — keep the entry but force ``status = "deprecated"``.
  Requires ``comment``.
- ``comment`` (str) — why the entry exists. These are observations of upstream
  reality at a point in time; undated, uncommented entries rot.

Every other key is a **template-var override**, shallow-merged over the vars
the populator built (``supports_tools = false``, ``supports_vision = false``,
…). Overrides win over fetched metadata by definition.

Populator integration (two lines plus the filter)::

    from unitysvc_sellers.model_overrides import load_model_overrides

    overrides = load_model_overrides(services_dir)        # services/model_overrides.toml
    models = [m for m in models if not overrides.skip(m["id"])]
    ...
    template_vars = overrides.apply(model_id, template_vars)
    ...
    overrides.warn_unmatched({m["id"] for m in models} | local_catalog_ids)
"""

from __future__ import annotations

import logging
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

OVERRIDES_FILENAME = "model_overrides.toml"

#: Keys with reserved semantics — everything else in an entry is a
#: template-var override.
RESERVED_KEYS = frozenset({"skip", "deprecated", "comment"})

#: Reserved keys whose presence demands a ``comment`` explaining why.
_COMMENT_REQUIRED = frozenset({"skip", "deprecated"})

#: Sub-table names reserved for a future v2: spec-shaped deep merges applied
#: to the RENDERED offering/listing JSON (``[models."x".offering.details]``
#: context_length = 32768) rather than to template vars. Rejected today so a
#: v1 file can never silently mean something different under v2. Flat keys
#: stay template-var overrides in both versions — they are render *inputs*
#: (template conditionals key on them, e.g. which documents attach), which a
#: post-render merge cannot express.
_SPEC_RESERVED = frozenset({"offering", "listing", "provider"})


@dataclass
class ModelOverrides:
    """Parsed ``model_overrides.toml`` with the convention's semantics."""

    entries: dict[str, dict[str, Any]] = field(default_factory=dict)
    path: Path | None = None

    def skip(self, model_id: str) -> bool:
        """True when the model must be excluded from the fetched list."""
        return bool(self.entries.get(model_id, {}).get("skip"))

    def apply(self, model_id: str, template_vars: dict[str, Any]) -> dict[str, Any]:
        """Return ``template_vars`` with this model's overrides merged in.

        ``deprecated = true`` forces ``status = "deprecated"``; every
        non-reserved key is shallow-merged over the built vars. The input dict
        is not mutated.
        """
        entry = self.entries.get(model_id)
        if not entry:
            return template_vars
        merged = dict(template_vars)
        if entry.get("deprecated"):
            merged["status"] = "deprecated"
        for key, value in entry.items():
            if key in RESERVED_KEYS:
                continue
            merged[key] = value
        return merged

    def warn_unmatched(self, known_model_ids: set[str]) -> list[str]:
        """Log (and return) override entries matching no known model.

        Call with the union of fetched model ids and locally cataloged ids —
        a stale entry usually means the model was renamed or finally delisted
        and the override can be retired.
        """
        stale = sorted(set(self.entries) - set(known_model_ids))
        for model_id in stale:
            logger.warning(
                "%s: override entry %r matches no fetched or cataloged model — retire it?",
                self.path or OVERRIDES_FILENAME,
                model_id,
            )
        return stale


def load_model_overrides(services_dir: str | Path) -> ModelOverrides:
    """Load ``<services_dir>/model_overrides.toml`` (missing file ⇒ no-op).

    Raises ``ValueError`` on a malformed file: a non-table entry, a reserved
    flag that isn't a bool, or a ``skip``/``deprecated`` entry without the
    required ``comment``. Fail-loud is deliberate — this file exists to encode
    human corrections, and silently ignoring a typo'd one re-breaks whatever
    the entry was fixing.
    """
    path = Path(services_dir) / OVERRIDES_FILENAME
    if not path.exists():
        return ModelOverrides()

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    models = raw.get("models", {})
    if not isinstance(models, dict):
        raise ValueError(f"{path}: [models] must be a table of per-model tables")

    entries: dict[str, dict[str, Any]] = {}
    for model_id, entry in models.items():
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: models.{model_id!r} must be a table, got {type(entry).__name__}")
        for flag in _COMMENT_REQUIRED:
            if flag in entry and not isinstance(entry[flag], bool):
                raise ValueError(f"{path}: models.{model_id!r}.{flag} must be a boolean")
        if any(entry.get(flag) for flag in _COMMENT_REQUIRED) and not str(entry.get("comment", "")).strip():
            raise ValueError(
                f"{path}: models.{model_id!r} sets skip/deprecated and must carry a non-empty comment explaining why"
            )
        spec_shaped = _SPEC_RESERVED & set(entry)
        if spec_shaped:
            raise ValueError(
                f"{path}: models.{model_id!r} uses {sorted(spec_shaped)} — these "
                "sub-tables are reserved for future spec-shaped merges and are "
                "not honored yet; use flat template-var keys instead"
            )
        entries[model_id] = dict(entry)

    unknown_top = set(raw) - {"models"}
    if unknown_top:
        logger.warning(
            "%s: ignoring unknown top-level key(s): %s",
            path,
            ", ".join(sorted(unknown_top)),
        )
    return ModelOverrides(entries=entries, path=path)
