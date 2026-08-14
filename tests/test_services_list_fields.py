"""Tests for `services list` column selection (`--fields` delta syntax) and the
revision-adjacent sort."""

from unitysvc_sellers.commands.services import (
    _DEFAULT_LIST_FIELDS,
    _list_sort_key,
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


class TestPreferRevisions:
    def test_original_skipped_when_its_revision_matches(self) -> None:
        from unitysvc_sellers.commands.tests import _prefer_revisions

        matched = [
            ("orig-id", "bedrock/m", None),
            ("rev-id", "bedrock/m", "orig-id"),
            ("other-id", "bedrock/n", None),
        ]
        targets, skipped = _prefer_revisions(matched)
        assert ("rev-id", "bedrock/m") in targets
        assert ("other-id", "bedrock/n") in targets
        assert targets == [t for t in targets if t[0] != "orig-id"]
        assert skipped == [("orig-id", "bedrock/m")]

    def test_no_revisions_keeps_everything(self) -> None:
        from unitysvc_sellers.commands.tests import _prefer_revisions

        matched = [("a", "x", None), ("b", "y", None)]
        targets, skipped = _prefer_revisions(matched)
        assert targets == [("a", "x"), ("b", "y")]
        assert skipped == []

    def test_revision_whose_original_is_not_matched_runs(self) -> None:
        # A revision matched alone (original filtered out server-side or named
        # directly) still runs; nothing is skipped.
        from unitysvc_sellers.commands.tests import _prefer_revisions

        matched = [("rev-id", "bedrock/m", "unmatched-orig")]
        targets, skipped = _prefer_revisions(matched)
        assert targets == [("rev-id", "bedrock/m")]
        assert skipped == []
