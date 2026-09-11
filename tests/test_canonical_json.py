"""Every writer that persists a seller data file must emit the same bytes
``usvc_seller specs format`` would.

The two sides disagreed on ``ensure_ascii``: ``format_data`` re-emits JSON with
``ensure_ascii=False``, while the write-back paths used a bare
``json.dumps(data, indent=2, sort_keys=True)``, whose default escapes non-ASCII.
A service whose ``display_name`` carried an em dash therefore got a
``service.json`` that could never pass ``specs format --check`` — see
unitysvc-labs/unitysvc-services-http#31, where it took CI red on an unrelated PR.

The invariant these tests lock in is the round trip, not the spelling: whatever a
writer puts on disk, ``format_data_files(check_only=True)`` must already accept.
"""

from pathlib import Path

from unitysvc_sellers.format_data import format_data_files
from unitysvc_sellers.params_render import sidecar_for_param, write_service_id_for_param
from unitysvc_sellers.utils import dump_canonical_json, write_service_data

# The exact display_name that broke unitysvc-services-http CI.
EM_DASH_NAME = "HTTP-to-SMTP — Bring Your Own SMTP Server"


def test_dump_canonical_json_is_a_fixed_point_of_the_formatter(tmp_path: Path) -> None:
    """The shared encoder's output is already canonical — this is the drift guard
    that keeps ``dump_canonical_json`` and ``format_data`` from diverging again."""
    payload = {"name": "z", "display_name": EM_DASH_NAME, "a": 1, "nested": {"é": "ü"}}

    (tmp_path / "service.json").write_text(dump_canonical_json(payload))

    assert format_data_files(tmp_path, check_only=True) is True


def test_write_service_data_emits_non_ascii_literally(tmp_path: Path) -> None:
    write_service_data(tmp_path, {"name": "http-to-smtp", "display_name": EM_DASH_NAME})

    content = (tmp_path / "service.json").read_text()
    assert "\\u2014" not in content
    assert EM_DASH_NAME in content


def test_write_service_data_output_needs_no_formatting(tmp_path: Path) -> None:
    write_service_data(tmp_path, {"name": "http-to-smtp", "display_name": EM_DASH_NAME})

    assert format_data_files(tmp_path, check_only=True) is True


def test_write_service_data_merge_does_not_re_escape_existing_keys(tmp_path: Path) -> None:
    """The upload write-back merges a service_id onto a sidecar someone else
    wrote; the keys it merely preserves must survive unescaped too."""
    write_service_data(tmp_path, {"display_name": EM_DASH_NAME})

    write_service_data(tmp_path, {"service_id": "e9021697-b792-4016-b162-bc0382b1dc57"})

    assert format_data_files(tmp_path, check_only=True) is True


def test_param_sidecar_write_back_output_needs_no_formatting(tmp_path: Path) -> None:
    """Param-file repos take the ``params_render`` sidecar path on upload rather
    than ``write_service_data`` — it has to hold the same invariant."""
    param_file = tmp_path / "http-to-smtp.json"
    param_file.write_text(dump_canonical_json({"parameters": {}}))
    sidecar_for_param(param_file).write_text(dump_canonical_json({"display_name": EM_DASH_NAME}))

    write_service_id_for_param(param_file, "e9021697-b792-4016-b162-bc0382b1dc57")

    assert format_data_files(tmp_path, check_only=True) is True
