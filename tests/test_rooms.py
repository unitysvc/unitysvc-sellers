"""Room facade wire contracts and typed parsing, through real generated clients."""

import inspect
import json

import httpx
import pytest

from unitysvc_sellers import AsyncClient, Client
from unitysvc_sellers.exceptions import NotFoundError

ROOM = "11111111-1111-4111-8111-111111111111"
MEMBER = "22222222-2222-4222-8222-222222222222"
CODE = "33333333-3333-4333-8333-333333333333"
MESSAGE = "44444444-4444-4444-8444-444444444444"
AT = "2026-10-30T00:00:00Z"


def summary(**overrides):
    return {
        "id": ROOM,
        "member_id": MEMBER,
        "kind": "helpdesk",
        "name": "Help desk",
        "handle": "helpdesk",
        "status": "active",
        "role": "owner",
        "created_at": AT,
        "description": "Talk with **support**",
        "owner_name": "Acme",
        "keep_forever": True,
        "fixed_membership": True,
        "can_manage": True,
        **overrides,
    }


def invitation():
    return {
        "id": CODE,
        "token": "ABCDEF",
        "role": "member",
        "status": "active",
        "use_count": 0,
        "max_uses": 3,
        "expires_at": AT,
        "created_at": AT,
    }


def transport(captured):
    def handler(request):
        captured.append(request)
        path = request.url.path
        if path.endswith("/missing"):
            return httpx.Response(404, json={"detail": "Room not found"})
        if path.endswith("/delivery"):
            settings = {"notify": "auto", "email": "off", "can_edit": True}
            if request.method == "PATCH":
                settings.update(json.loads(request.content))
            return httpx.Response(200, json=settings)
        if path.endswith("/codes"):
            return httpx.Response(
                201 if request.method == "POST" else 200,
                json=invitation() if request.method == "POST" else {"data": [invitation()]},
            )
        if "/codes/" in path:
            return httpx.Response(200, json={**invitation(), "status": "revoked"})
        if path.endswith("/members"):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": MEMBER,
                            "account_type": "seller",
                            "account_id": ROOM,
                            "name": "Acme",
                            "role": "owner",
                            "joined_at": AT,
                        }
                    ]
                },
            )
        if path.endswith("/join"):
            return httpx.Response(200, json=summary())
        if request.method == "POST":
            return httpx.Response(202, json={"room_id": ROOM, "message_id": MESSAGE, "offset": 42, "routed": "handle"})
        if request.method == "PATCH":
            return httpx.Response(200, json=summary(**json.loads(request.content)))
        if path.endswith("/rooms"):
            return httpx.Response(200, json={"data": [summary()]})
        return httpx.Response(200, json={**summary(), "messages": {"data": [], "next": 41}})

    return httpx.MockTransport(handler)


def client_for(asynchronous, captured):
    cls = AsyncClient if asynchronous else Client
    client = cls(api_key="svcpass_test", base_url="https://test.example/v1/seller")
    if asynchronous:
        client._client.get_async_httpx_client()._transport = transport(captured)
    else:
        client._client.get_httpx_client()._transport = transport(captured)
    return client


async def call(resource, method, *args, **kwargs):
    result = getattr(resource, method)(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


async def close(client, asynchronous):
    if asynchronous:
        await client.aclose()
    else:
        client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("owner_sets_retention", [False, True])
async def test_indefinite_room_retention_policy_is_typed(asynchronous, owner_sets_retention):
    captured = []
    client = client_for(asynchronous, captured)
    policy = summary(
        kind="helpdesk" if not owner_sets_retention else "discussion",
        retention_seconds=None,
        max_retention_seconds=None,
        owner_sets_retention=owner_sets_retention,
    )

    def handler(request):
        captured.append(request)
        return httpx.Response(
            200,
            json={"data": [policy]}
            if request.url.path.endswith("/rooms")
            else {**policy, "messages": {"data": [], "next": None}},
        )

    wire = httpx.MockTransport(handler)
    if asynchronous:
        client._client.get_async_httpx_client()._transport = wire
    else:
        client._client.get_httpx_client()._transport = wire
    try:
        room = await call(client.rooms, "get", ROOM)
        listed = await call(client.rooms, "list")
        for parsed in [room, listed.data[0]]:
            assert parsed.retention_seconds is None
            assert parsed.max_retention_seconds is None
            assert parsed.owner_sets_retention is owner_sets_retention
            assert parsed.keep_forever is True
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_room_delivery_paths_and_partial_updates(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        delivery = await call(client.rooms, "delivery", ROOM)
        assert delivery.notify == "auto"
        assert delivery.email == "off"
        assert delivery.can_edit is True

        updated = await call(client.rooms, "set_delivery", ROOM, email="email")
        assert updated.email == "email"
        assert updated.notify == "auto"
        assert captured[-1].method == "PATCH"
        assert captured[-1].url.path.endswith(f"/rooms/{ROOM}/delivery")
        assert json.loads(captured[-1].content) == {"email": "email"}

        await call(client.rooms, "set_delivery", ROOM, notify="off", email="auto")
        assert json.loads(captured[-1].content) == {"notify": "off", "email": "auto"}
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_room_metadata_management_and_private_members(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        listed = await call(client.rooms, "list", kind="helpdesk")
        assert listed.data[0].owner_name == "Acme"
        room = await call(client.rooms, "get", "helpdesk", after=40, limit=20)
        assert room.description == "Talk with **support**"
        assert room.messages.next_ == 41
        changed = await call(client.rooms, "update", ROOM, description="# Our support", name="Support")
        assert changed.description == "# Our support"
        assert changed.name == "Support"
        await call(client.rooms, "update", ROOM, description=None)
        members = await call(client.rooms, "members", ROOM)
        assert members.data[0].name == "Acme"
        assert captured[0].url.params["kind"] == "helpdesk"
        assert captured[1].url.params["after"] == "40"
        assert json.loads(captured[2].content) == {"name": "Support", "description": "# Our support"}
        assert json.loads(captured[3].content) == {"description": None}
        assert captured[2].method == "PATCH"
        assert captured[4].url.path.endswith(f"/rooms/{ROOM}/members")
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_invitation_lifecycle_and_posting(asynchronous):
    captured = []
    client = client_for(asynchronous, captured)
    try:
        code = await call(client.rooms, "create_invitation", ROOM, role="member", max_uses=3)
        assert code.token == "ABCDEF"
        codes = await call(client.rooms, "invitations", ROOM, include_inactive=True)
        assert len(codes.data) == 1
        joined = await call(client.rooms, "join", "ABCDEF")
        assert str(joined.id) == ROOM
        revoked = await call(client.rooms, "revoke_invitation", ROOM, CODE)
        assert revoked.status == "revoked"
        posted = await call(client.rooms, "post", "helpdesk", body="Help", client_message_id="test-1")
        assert posted.offset == 42
        await call(client.rooms, "post", body="@helpdesk Help")
        assert captured[3].method == "DELETE"
        assert captured[4].url.path.endswith("/rooms/helpdesk")
        assert captured[5].url.path.endswith("/rooms")
        assert json.loads(captured[4].content)["client_message_id"] == "test-1"
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_room_errors_are_sdk_errors(asynchronous):
    client = client_for(asynchronous, [])
    try:
        with pytest.raises(NotFoundError):
            await call(client.rooms, "get", "missing")
    finally:
        await close(client, asynchronous)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_owner_status_and_pause_message_reach_the_wire(asynchronous):
    """rooms.update sends the operational status and auto-reply (#2843 S5b)."""
    captured = []
    client = client_for(asynchronous, captured)
    try:
        changed = await call(client.rooms, "update", ROOM, status="paused", pause_message="Back Monday")
        assert json.loads(captured[-1].content) == {"status": "paused", "pause_message": "Back Monday"}
        assert changed.status == "paused"
        assert changed.pause_message == "Back Monday"
        await call(client.rooms, "update", ROOM, status="active", pause_message=None)
        assert json.loads(captured[-1].content) == {"status": "active", "pause_message": None}
    finally:
        await close(client, asynchronous)
