"""Tests for `services list` column selection (`--fields` delta syntax) and the
revision-adjacent sort."""

from datetime import UTC

from unitysvc_sellers.commands.services import (
    _DEFAULT_LIST_FIELDS,
    _is_time_column,
    _list_sort_key,
    _relative_age,
    _resolve_fields,
)


class TestResolveFields:
    def test_absolute_list_replaces_defaults(self) -> None:
        assert _resolve_fields("id,name,status") == ["id", "name", "status"]

    def test_default_string_yields_defaults(self) -> None:
        assert _resolve_fields(",".join(_DEFAULT_LIST_FIELDS)) == _DEFAULT_LIST_FIELDS

    def test_empty_yields_defaults(self) -> None:
        assert _resolve_fields("") == _DEFAULT_LIST_FIELDS

    def test_delta_append(self) -> None:
        assert _resolve_fields("+created_at") == [*_DEFAULT_LIST_FIELDS, "created_at"]

    def test_delta_remove(self) -> None:
        assert _resolve_fields("-visibility") == [f for f in _DEFAULT_LIST_FIELDS if f != "visibility"]

    def test_delta_append_and_remove(self) -> None:
        result = _resolve_fields("+created_at,-service_type")
        assert "created_at" in result and "service_type" not in result

    def test_delta_append_already_present_is_noop(self) -> None:
        # revision_of is already a default, so +revision_of changes nothing.
        assert _resolve_fields("+revision_of") == _DEFAULT_LIST_FIELDS

    def test_delta_remove_absent_is_noop(self) -> None:
        assert _resolve_fields("-not_a_column") == _DEFAULT_LIST_FIELDS


class TestListSortKey:
    def test_revision_sorts_directly_after_its_original(self) -> None:
        original = {"name": "prov/model", "id": "aaa", "revision_of": None}
        revision = {"name": "prov/model", "id": "bbb", "revision_of": "aaa"}
        other = {"name": "prov/another", "id": "ccc", "revision_of": None}
        rows = sorted([revision, other, original], key=_list_sort_key)
        # grouped by name ('another' < 'model'); within a name, original before revision
        assert [r["id"] for r in rows] == ["ccc", "aaa", "bbb"]


class TestSkipActive:
    def test_active_services_skipped_by_default(self) -> None:
        from unitysvc_sellers.commands.tests import _skip_active

        matched = [
            ("orig-id", "bedrock/m", "active"),
            ("rev-id", "bedrock/m", "draft"),
            ("other-id", "bedrock/n", "rejected"),
        ]
        targets, skipped = _skip_active(matched)
        assert targets == [("rev-id", "bedrock/m"), ("other-id", "bedrock/n")]
        assert skipped == [("orig-id", "bedrock/m")]

    def test_only_active_matches_yields_no_targets(self) -> None:
        # Mirrors submit: a name matching only an active service tests nothing.
        from unitysvc_sellers.commands.tests import _skip_active

        matched = [("a", "x", "active")]
        targets, skipped = _skip_active(matched)
        assert targets == []
        assert skipped == [("a", "x")]

    def test_no_active_keeps_everything(self) -> None:
        from unitysvc_sellers.commands.tests import _skip_active

        matched = [("a", "x", "draft"), ("b", "y", "pending"), ("c", "z", None)]
        targets, skipped = _skip_active(matched)
        assert targets == [("a", "x"), ("b", "y"), ("c", "z")]
        assert skipped == []


class TestRelativeAge:
    """Timestamps render as a scannable one-unit age (table only; JSON keeps raw)."""

    @staticmethod
    def _iso(**delta: float) -> str:
        from datetime import datetime, timedelta

        return (datetime.now(UTC) - timedelta(**delta)).isoformat()

    def test_sub_minute_reads_just_now(self) -> None:
        assert _relative_age(self._iso(seconds=5)) == "just now"

    def test_minutes_hours_days(self) -> None:
        assert _relative_age(self._iso(minutes=42)) == "42m ago"
        assert _relative_age(self._iso(hours=5)) == "5h ago"
        assert _relative_age(self._iso(days=3)) == "3d ago"

    def test_months_and_years(self) -> None:
        assert _relative_age(self._iso(days=75)) == "2mo ago"
        assert _relative_age(self._iso(days=800)) == "2y ago"

    def test_zulu_suffix_parses(self) -> None:
        # The API may serialize UTC as ``…Z``; fromisoformat needs +00:00.
        from datetime import datetime, timedelta

        stamp = (datetime.now(UTC) - timedelta(hours=2)).replace(tzinfo=None)
        assert _relative_age(stamp.isoformat() + "Z") == "2h ago"

    def test_naive_timestamp_assumed_utc(self) -> None:
        from datetime import datetime, timedelta

        naive = (datetime.now(UTC) - timedelta(days=1)).replace(tzinfo=None)
        assert _relative_age(naive.isoformat()) == "1d ago"

    def test_future_timestamp_does_not_crash(self) -> None:
        # Clock skew between API and CLI host: never render a negative age.
        assert _relative_age(self._iso(seconds=-30)) == "just now"

    def test_unparseable_value_passes_through(self) -> None:
        # A listing must not fail on a timestamp surprise.
        assert _relative_age("not-a-timestamp") == "not-a-timestamp"

    def test_only_at_columns_are_treated_as_times(self) -> None:
        assert _is_time_column("updated_at") and _is_time_column("created_at")
        assert not _is_time_column("status") and not _is_time_column("name")


class TestUpdatedIsADefaultColumn:
    def test_updated_at_is_shown_by_default(self) -> None:
        assert "updated_at" in _DEFAULT_LIST_FIELDS
        assert _resolve_fields("") == _DEFAULT_LIST_FIELDS

    def test_it_can_be_dropped_with_a_delta(self) -> None:
        assert "updated_at" not in _resolve_fields("-updated_at")

    def test_header_reads_updated(self) -> None:
        from unitysvc_sellers.commands.services import _COLUMN_LABELS

        assert _COLUMN_LABELS["updated_at"] == "updated"
