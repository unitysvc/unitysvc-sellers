"""Tests for ``usvc seller rooms`` (unitysvc#2846 C8).

``async_client`` is monkeypatched with a recording sink, so no backend is
needed: each command must call the right ``client.rooms`` method with the
right arguments and print its result.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from types import SimpleNamespace
from typing import Any

import pytest
from typer.testing import CliRunner

from unitysvc_sellers.commands.rooms import app

runner = CliRunner()

ROOM = {
    "id": "11111111-1111-4111-8111-111111111111",
    "kind": "chat",
    "name": "Book club",
    "handle": "book-club",
    "role": "owner",
    "status": "active",
}


class _Rooms:
    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []

    async def list(self, **filters: Any) -> Any:
        self.calls.append(("list", filters))
        return SimpleNamespace(data=[ROOM])

    async def get(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("get", target, kwargs))
        message = {"offset": 3, "sent_at": "2026-10-31T10:00:00Z", "sender_name": "Ann", "body": "hello"}
        return {**ROOM, "description": "Read together", "messages": {"data": [message], "next": 3}}

    async def post(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("post", target, kwargs))
        return {"room_id": ROOM["id"], "offset": 4}

    async def members(self, target: str) -> Any:
        self.calls.append(("members", target))
        return SimpleNamespace(data=[{"name": "Ann", "account_type": "customer", "role": "owner", "joined_at": "x"}])

    async def update(self, target: str, **settings: Any) -> dict[str, Any]:
        self.calls.append(("update", target, settings))
        return {**ROOM, **settings}

    async def delivery(self, target: str) -> dict[str, Any]:
        self.calls.append(("delivery", target))
        return {"notify": "auto", "email": "off", "can_edit": True}

    async def set_delivery(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("set_delivery", target, kwargs))
        return {"notify": kwargs["notify"] or "auto", "email": kwargs["email"] or "off", "can_edit": True}

    async def create_invitation(self, target: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(("create_invitation", target, kwargs))
        return {"token": "ABCD1234", "role": kwargs["role"]}

    async def invitations(self, target: str, **kwargs: Any) -> Any:
        self.calls.append(("invitations", target, kwargs))
        return SimpleNamespace(data=[{"id": "c1", "token": "ABCD1234"}])

    async def revoke_invitation(self, target: str, code_id: str) -> dict[str, Any]:
        self.calls.append(("revoke_invitation", target, code_id))
        return {"id": code_id, "status": "revoked"}

    async def join(self, token: str) -> dict[str, Any]:
        self.calls.append(("join", token))
        return ROOM

    async def leave(self, target: str) -> None:
        self.calls.append(("leave", target))


@pytest.fixture
def rooms(monkeypatch: pytest.MonkeyPatch) -> _Rooms:
    sink = _Rooms()

    @asynccontextmanager
    async def fake_async_client(api_key=None, base_url=None):  # type: ignore[no-untyped-def]
        yield SimpleNamespace(rooms=sink)

    monkeypatch.setattr("unitysvc_sellers.commands.rooms.async_client", fake_async_client)
    return sink


def test_list_passes_the_filters(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["list", "--kind", "chat", "--enrollment", "e1", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert rooms.calls == [("list", {"kind": "chat", "enrollment": "e1", "service": None})]
    assert json.loads(result.output)[0]["handle"] == "book-club"
    table = runner.invoke(app, ["list", "--service", "s1"])
    assert table.exit_code == 0 and "Book club" in table.output
    assert rooms.calls[-1] == ("list", {"kind": None, "enrollment": None, "service": "s1"})


def test_show_prints_messages_and_the_next_cursor(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["show", "me", "--after", "2", "--limit", "10"])
    assert result.exit_code == 0, result.output
    assert rooms.calls == [("get", "me", {"after": 2, "limit": 10})]
    assert "Ann" in result.output and "hello" in result.output and "--after 3" in result.output


def test_post_members_and_settings(rooms: _Rooms) -> None:
    assert runner.invoke(app, ["post", "book-club", "hi all", "--id", "k1"]).exit_code == 0
    assert rooms.calls[-1] == ("post", "book-club", {"body": "hi all", "client_message_id": "k1"})
    assert "Ann" in runner.invoke(app, ["members", "book-club"]).output
    result = runner.invoke(app, ["set", "book-club", "--status", "readonly", "--retention", "3600"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("update", "book-club", {"retention_seconds": 3600, "status": "readonly"})
    assert runner.invoke(app, ["set", "book-club"]).exit_code == 1


def test_delivery_reads_or_changes(rooms: _Rooms) -> None:
    assert json.loads(runner.invoke(app, ["delivery", "me"]).output)["notify"] == "auto"
    result = runner.invoke(app, ["delivery", "me", "--email", "auto"])
    assert result.exit_code == 0, result.output
    assert rooms.calls[-1] == ("set_delivery", "me", {"notify": None, "email": "auto"})


def test_invitations_join_and_leave(rooms: _Rooms) -> None:
    result = runner.invoke(app, ["invite", "book-club", "--role", "moderator", "--max-uses", "5"])
    assert result.exit_code == 0 and "ABCD1234" in result.output
    assert rooms.calls[-1] == ("create_invitation", "book-club", {"role": "moderator", "max_uses": 5})
    assert runner.invoke(app, ["invitations", "book-club", "--all"]).exit_code == 0
    assert rooms.calls[-1] == ("invitations", "book-club", {"include_inactive": True})
    assert runner.invoke(app, ["revoke", "book-club", "c1"]).exit_code == 0
    assert "@book-club" in runner.invoke(app, ["join", "ABCD1234"]).output
    assert runner.invoke(app, ["leave", "book-club", "--yes"]).exit_code == 0
    assert rooms.calls[-1] == ("leave", "book-club")
