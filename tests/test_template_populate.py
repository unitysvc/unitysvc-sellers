"""Tests for ``unitysvc_sellers.template_populate``.

Locks in the flat ``specs/`` behaviour of ``populate_from_iterator`` (#1263):
nested folder paths matching ``listing.name``, a static ``provider.json``
copied into every folder, idempotent regeneration (``time_created`` preserved),
and recursive deprecation of services no longer offered upstream.
"""

import json
from pathlib import Path

from unitysvc_sellers.template_populate import populate_from_iterator

OFFERING_TPL = """{
  "name": "{{ offering_name }}",
  "display_name": "{{ display_name }}",
  "service_type": "{{ service_type }}",
  "status": "{{ status | default('ready') }}"
}
"""

LISTING_TPL = """{
  "name": "{{ name }}",
  "status": "{{ status | default('ready') }}"
}
"""

PROVIDER_JSON = {
    "name": "acme",
    "display_name": "Acme",
    "status": "ready",
    "time_created": "2025-01-01T00:00:00Z",
}


def _setup_templates(tmp_path: Path, *, with_provider: bool = True) -> Path:
    tpl = tmp_path / "templates"
    tpl.mkdir()
    (tpl / "offering.json.j2").write_text(OFFERING_TPL)
    (tpl / "listing.json.j2").write_text(LISTING_TPL)
    if with_provider:
        (tpl / "provider.json").write_text(json.dumps(PROVIDER_JSON) + "\n")
    return tpl


def _model(name: str) -> dict:
    return {
        "name": name,
        "offering_name": name.split("/")[-1],
        "display_name": name.split("/")[-1].title(),
        "service_type": "llm",
    }


def test_nested_folders_and_provider_copy(tmp_path: Path) -> None:
    _setup_templates(tmp_path)
    specs = tmp_path / "specs"

    stats = populate_from_iterator(
        iter([_model("acme/foo"), _model("acme/org/bar")]),
        templates_dir=tmp_path / "templates",
        output_dir=specs,
    )

    assert stats["written"] == 2
    # '/' is preserved -> nested folder paths equal the service name
    foo = specs / "acme" / "foo"
    bar = specs / "acme" / "org" / "bar"
    assert (foo / "offering.json").exists()
    assert (bar / "listing.json").exists()
    # provider.json copied verbatim into each folder
    for d in (foo, bar):
        assert json.loads((d / "provider.json").read_text()) == PROVIDER_JSON
    # listing.name == folder path under specs/
    assert json.loads((bar / "listing.json").read_text())["name"] == "acme/org/bar"


def test_idempotent_regen_preserves_time_created(tmp_path: Path) -> None:
    _setup_templates(tmp_path)
    specs = tmp_path / "specs"

    populate_from_iterator(iter([_model("acme/foo")]), tmp_path / "templates", specs)
    listing = specs / "acme" / "foo" / "listing.json"
    stamp = json.loads(listing.read_text())["time_created"]

    # Second run: no content change -> skipped, stamp unchanged
    stats = populate_from_iterator(iter([_model("acme/foo")]), tmp_path / "templates", specs)
    assert stats["skipped"] == 1
    assert stats["written"] == 0
    assert json.loads(listing.read_text())["time_created"] == stamp


def test_deprecates_missing_nested_service(tmp_path: Path) -> None:
    _setup_templates(tmp_path)
    specs = tmp_path / "specs"

    # First run creates two services
    populate_from_iterator(
        iter([_model("acme/foo"), _model("acme/org/bar")]),
        tmp_path / "templates",
        specs,
    )
    # Second run drops bar -> bar should be deprecated (offering + listing)
    stats = populate_from_iterator(iter([_model("acme/foo")]), tmp_path / "templates", specs)
    assert stats["deprecated"] == 1

    bar = specs / "acme" / "org" / "bar"
    assert json.loads((bar / "offering.json").read_text())["status"] == "deprecated"
    assert json.loads((bar / "listing.json").read_text())["status"] == "deprecated"
    # foo untouched
    assert json.loads((specs / "acme" / "foo" / "offering.json").read_text())["status"] == "ready"


def test_no_provider_template_is_graceful(tmp_path: Path) -> None:
    _setup_templates(tmp_path, with_provider=False)
    specs = tmp_path / "specs"

    stats = populate_from_iterator(iter([_model("acme/foo")]), tmp_path / "templates", specs)
    assert stats["written"] == 1
    assert not (specs / "acme" / "foo" / "provider.json").exists()
