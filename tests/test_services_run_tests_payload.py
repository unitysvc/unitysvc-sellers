"""Tests for ``_parse_run_tests_payload`` — the task-payload → typed-result coercion.

Pins the per-channel breakdown (#1281/#1297): the diagnostic probes each
upstream access channel, so a failing row carries ``upstream_channels`` keyed
by channel name alongside the back-compat singleton ``upstream``.
"""

from __future__ import annotations

from unitysvc_sellers.services import _parse_run_tests_payload


def test_parses_upstream_channels_per_row() -> None:
    payload = {
        "status": "success",
        "result": {
            "service_id": "svc-1",
            "status": "failure",
            "success_count": 0,
            "fail_count": 1,
            "skipped_count": 0,
            "results": [
                {
                    "document_id": "doc-1",
                    "interface_name": "default",
                    "status": "script_failed",
                    "outcome": "upstream_fault",
                    "upstream": {"status": "script_failed"},
                    "upstream_channels": {
                        "http_relay": {"status": "success"},
                        "plus": {"status": "script_failed"},
                    },
                }
            ],
        },
    }

    result = _parse_run_tests_payload("task-1", payload)

    assert len(result.results) == 1
    row = result.results[0]
    assert row.upstream == {"status": "script_failed"}
    assert row.upstream_channels == {
        "http_relay": {"status": "success"},
        "plus": {"status": "script_failed"},
    }


def test_upstream_channels_absent_is_none() -> None:
    payload = {
        "status": "success",
        "result": {
            "service_id": "svc-1",
            "status": "success",
            "results": [{"document_id": "doc-1", "status": "success"}],
        },
    }

    row = _parse_run_tests_payload("task-1", payload).results[0]
    assert row.upstream_channels is None
