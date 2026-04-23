"""End-to-end coverage of ``$doc_preset`` / ``$file_preset`` flowing
through the seller pipeline.

The sentinel walker and its unit tests live in ``unitysvc-core`` —
`unitysvc_core.utils.load_data_file` expands every ``$<fn>`` sentinel
after the override merge, driven by the registry in
``unitysvc_data.PRESET_FNS``. These tests only cover the seller-side
integration: that the expanded records survive ``_resolve_file_references``
and that the historical relative-``file_path`` shape still works for
catalogs that haven't migrated to presets.
"""

from __future__ import annotations

import json
from pathlib import Path

from unitysvc_sellers.upload import _resolve_file_references
from unitysvc_sellers.utils import load_data_file


def test_preset_expanded_doc_survives_resolve_file_references(tmp_path: Path):
    """Load a listing with a ``$doc_preset`` sentinel, then resolve file refs.

    Verifies the full pipeline: core's ``load_data_file`` expands the
    sentinel to a record with an absolute ``file_path`` (pointing
    inside the installed ``unitysvc-data`` package), then
    ``_resolve_file_references`` reads+renders the file, inlines its
    content as ``file_content``, and stores just the basename as the
    displayable ``file_path``.
    """
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

    The stored ``file_path`` keeps the relative shape (minus ``.j2``)
    so catalogs that haven't migrated to presets aren't disrupted by
    the absolute-path branch added alongside preset expansion.
    """
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
