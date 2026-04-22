"""Tests for ``expand_presets`` and the preset-aware ``load_data_file`` wrapper.

Sellers can embed ``{"$doc_preset": ...}`` / ``{"$file_preset": ...}``
sentinels anywhere in a JSON/TOML data file. The walker in
``unitysvc_sellers.utils`` replaces each sentinel with the expanded
value from ``unitysvc-data`` at load time, so the rest of the upload /
validate pipeline sees fully-materialised records.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from unitysvc_data import doc_preset

from unitysvc_sellers.utils import (
    SELLER_PRESET_FNS,
    expand_presets,
    load_data_file,
)

# ---------------------------------------------------------------------------
# expand_presets — sentinel detection and replacement
# ---------------------------------------------------------------------------


def test_bare_string_doc_preset_sentinel_expands_to_document_record():
    node = {"Connectivity": {"$doc_preset": "s3_connectivity"}}
    result = expand_presets(node)
    record = result["Connectivity"]
    assert record["category"] == "connectivity_test"
    assert record["mime_type"] == "python"
    assert Path(record["file_path"]).is_file()


def test_doc_preset_alias_matches_versioned():
    alias = expand_presets({"x": {"$doc_preset": "s3_connectivity"}})["x"]
    versioned = expand_presets({"x": {"$doc_preset": "s3_connectivity_v1"}})["x"]
    assert alias == versioned


def test_doc_preset_sentinel_with_with_block_forwards_overrides():
    # The sentinel's VALUE is forwarded to doc_preset verbatim. doc_preset
    # already understands the nested {"$preset": ..., "$with": {...}} form,
    # so overrides travel through cleanly.
    node = {
        "$doc_preset": {
            "$preset": "s3_code_example",
            "$with": {"description": "Uploads to customer bucket", "is_public": False},
        }
    }
    record = expand_presets(node)
    assert record["description"] == "Uploads to customer bucket"
    assert record["is_public"] is False
    assert record["category"] == "usage_example"


def test_file_preset_sentinel_returns_raw_content():
    node = {"$file_preset": "s3_connectivity_v1"}
    content = expand_presets(node)
    assert isinstance(content, str)
    assert "boto3" in content


def test_expand_presets_walks_nested_dicts_and_lists():
    data = {
        "documents": {
            "Connectivity": {"$doc_preset": "s3_connectivity_v1"},
            "Custom": {"category": "custom", "file_path": "local.sh"},
        },
        "snippets": [
            {"$file_preset": "s3_connectivity_v1"},
            "plain string",
            {"nested": {"$doc_preset": "api_connectivity"}},
        ],
    }
    result = expand_presets(data)

    # Preset nodes replaced.
    assert result["documents"]["Connectivity"]["category"] == "connectivity_test"
    assert isinstance(result["snippets"][0], str)
    assert result["snippets"][1] == "plain string"
    assert result["snippets"][2]["nested"]["category"] == "connectivity_test"

    # Non-sentinel dicts pass through unchanged.
    assert result["documents"]["Custom"] == {"category": "custom", "file_path": "local.sh"}


def test_expand_presets_returns_fresh_structure_and_does_not_mutate_input():
    original = {"a": {"$doc_preset": "s3_connectivity_v1"}, "b": [1, 2, 3]}
    before = json.dumps(original, sort_keys=True)
    expand_presets(original)
    after = json.dumps(original, sort_keys=True)
    assert before == after, "expand_presets must not mutate its input"


def test_sentinel_alongside_other_keys_is_rejected_with_clear_error():
    # A sentinel must be the only key in its dict. Silently ignoring a
    # $doc_preset key next to a sibling would be a footgun, so we raise.
    node = {
        "$doc_preset": "s3_connectivity",
        "category": "overridden",  # siblings are not allowed
    }
    with pytest.raises(ValueError, match="must appear alone in its dict"):
        expand_presets(node)


def test_unknown_dollar_key_is_not_treated_as_sentinel():
    # $-prefixed keys that don't match a registered preset function are
    # treated as ordinary data (e.g. MongoDB operators in metadata).
    node = {"$eq": "s3_connectivity"}
    assert expand_presets(node) == {"$eq": "s3_connectivity"}


def test_unknown_preset_name_raises_from_underlying_function():
    with pytest.raises(KeyError, match="Unknown preset"):
        expand_presets({"$doc_preset": "no_such_preset"})


def test_scalars_pass_through_unchanged():
    for scalar in [None, True, 42, 3.14, "hello", "$doc_preset"]:
        assert expand_presets(scalar) == scalar


def test_custom_preset_fns_mapping_restricts_recognised_names():
    # Only ``my_fn`` is recognised; $doc_preset is ignored.
    def my_fn(arg: Any) -> dict[str, Any]:
        return {"expanded": arg}

    node = {
        "outer": {"$my_fn": "hello"},
        "ignored": {"$doc_preset": "s3_connectivity"},
    }
    result = expand_presets(node, preset_fns={"my_fn": my_fn})
    assert result["outer"] == {"expanded": "hello"}
    # $doc_preset is not in the custom mapping -> left unchanged.
    assert result["ignored"] == {"$doc_preset": "s3_connectivity"}


# ---------------------------------------------------------------------------
# load_data_file wrapper
# ---------------------------------------------------------------------------


def test_load_data_file_expands_presets_in_json(tmp_path: Path):
    listing = tmp_path / "listing.json"
    listing.write_text(
        json.dumps(
            {
                "schema": "listing_v1",
                "name": "demo",
                "documents": {
                    "Connectivity test": {"$doc_preset": "s3_connectivity_v1"},
                },
            }
        )
    )

    data, fmt = load_data_file(listing)
    assert fmt == "json"
    record = data["documents"]["Connectivity test"]
    assert record["category"] == "connectivity_test"
    assert record["mime_type"] == "python"
    assert Path(record["file_path"]).is_file()
    # Sentinel is fully replaced — no $-keys remain.
    assert "$doc_preset" not in record


def test_load_data_file_expands_presets_in_toml(tmp_path: Path):
    listing = tmp_path / "listing.toml"
    listing.write_text(
        'schema = "listing_v1"\n'
        'name = "demo"\n'
        '[documents."Connectivity test"]\n'
        '"$doc_preset" = "s3_connectivity_v1"\n'
    )

    data, fmt = load_data_file(listing)
    assert fmt == "toml"
    record = data["documents"]["Connectivity test"]
    assert record["category"] == "connectivity_test"
    assert "$doc_preset" not in record


def test_load_data_file_expands_presets_after_override_merge(tmp_path: Path):
    # Sentinel lives in the base file; override customises is_active.
    # Expansion happens *after* the merge, so the final doc is the
    # preset's record with the override applied.
    base = tmp_path / "listing.json"
    base.write_text(
        json.dumps(
            {
                "schema": "listing_v1",
                "documents": {
                    "Connectivity test": {
                        "$doc_preset": {
                            "$preset": "s3_connectivity_v1",
                            "$with": {"is_active": True},
                        }
                    }
                },
            }
        )
    )
    override = tmp_path / "listing.override.json"
    override.write_text(json.dumps({"name": "from-override"}))

    data, _ = load_data_file(base)
    assert data["name"] == "from-override"
    record = data["documents"]["Connectivity test"]
    assert record["is_active"] is True
    assert record["category"] == "connectivity_test"


def test_load_data_file_with_preset_fns_none_skips_expansion(tmp_path: Path):
    # Escape hatch: callers that explicitly don't want expansion can
    # disable it by passing preset_fns=None.
    listing = tmp_path / "listing.json"
    listing.write_text(
        json.dumps(
            {
                "schema": "listing_v1",
                "documents": {"Thing": {"$doc_preset": "s3_connectivity_v1"}},
            }
        )
    )

    data, _ = load_data_file(listing, preset_fns=None)
    # Sentinel survives — no expansion applied.
    assert data["documents"]["Thing"] == {"$doc_preset": "s3_connectivity_v1"}


def test_seller_preset_fns_registers_doc_and_file():
    assert set(SELLER_PRESET_FNS) == {"doc_preset", "file_preset"}
    # Factory identity: the registered callable is the imported function.
    assert SELLER_PRESET_FNS["doc_preset"] is doc_preset


# ---------------------------------------------------------------------------
# End-to-end: preset sentinel in a listing flows through the upload pipeline
# ---------------------------------------------------------------------------


def test_preset_expanded_doc_survives_resolve_file_references(tmp_path: Path):
    """Load a listing with a $doc_preset, then resolve file refs.

    Verifies the full pipeline: expand_presets converts the sentinel to
    a record with an absolute ``file_path`` (pointing inside the
    installed ``unitysvc-data`` package), then ``_resolve_file_references``
    reads+renders the file, inlines its content as ``file_content``,
    and stores just the basename as the displayable ``file_path``.
    """
    from unitysvc_sellers.upload import _resolve_file_references

    listing = tmp_path / "listing.json"
    listing.write_text(
        json.dumps(
            {
                "schema": "listing_v1",
                "name": "demo",
                "documents": {
                    "Connectivity": {"$doc_preset": "s3_connectivity_v1"},
                },
            }
        )
    )

    data, _ = load_data_file(listing)
    record_before = data["documents"]["Connectivity"]
    # Sanity: preset expansion produces an absolute path to the bundled file.
    assert Path(record_before["file_path"]).is_absolute()
    assert Path(record_before["file_path"]).is_file()

    resolved = _resolve_file_references(
        data,
        tmp_path,
        listing=data,
        provider={"name": "acme"},
        offering={"upstream_access_config": {"default": {"base_url": "https://s3.acme.test"}}},
        interface={"base_url": "https://s3.acme.test"},
    )
    record_after = resolved["documents"]["Connectivity"]

    # file_content is inlined — the backend never needs to open the file.
    assert "boto3" in record_after["file_content"]
    # file_path is reduced to basename (no absolute path leaked to backend),
    # and .j2 is stripped so the stored name matches the rendered output.
    assert record_after["file_path"] == "connectivity-v1.py"
    # Metadata carried through unchanged.
    assert record_after["category"] == "connectivity_test"
    assert record_after["mime_type"] == "python"


def test_relative_file_path_keeps_backwards_compatible_shape(tmp_path: Path):
    """Existing seller catalogs write relative paths like ``../../docs/foo.sh.j2``.

    The stored ``file_path`` still keeps the relative shape (minus
    ``.j2``) so existing catalogs aren't disrupted by the absolute-path
    support added for preset expansion.
    """
    from unitysvc_sellers.upload import _resolve_file_references

    provider_dir = tmp_path / "acme"
    docs_dir = provider_dir / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "shared.js.j2").write_text("// hi {{ provider.name }}\n")

    service_dir = provider_dir / "services" / "svc1"
    service_dir.mkdir(parents=True)

    data = {"file_path": "../../docs/shared.js.j2", "mime_type": "javascript"}
    resolved = _resolve_file_references(data, service_dir, provider={"name": "acme"})

    # Relative shape preserved — no change from pre-preset behaviour.
    assert resolved["file_path"] == "../../docs/shared.js"
    assert "hi acme" in resolved["file_content"]
