"""``usvc seller rooms`` — rooms the account can reach, their messages and settings.

Mirrors :class:`unitysvc_sellers.arooms.AsyncRooms`. ``ROOM`` is a room id or one of
the account's handles (``me``, ``helpdesk``, or a room's own handle):

- ``usvc seller rooms list [--kind K] [--enrollment ID] [--service ID]``
- ``usvc seller rooms show ROOM [--after N] [--limit N]``   — the room and its messages
- ``usvc seller rooms post ROOM TEXT [--title T] [--id KEY]``
- ``usvc seller rooms members ROOM``
- ``usvc seller rooms set ROOM [--name] [--description] [--retention S] [--status S]``
- ``usvc seller rooms delivery ROOM [--notify PATH] [--email PATH]``
- ``usvc seller rooms invite ROOM [--role R] [--max-uses N] [--expires-in-days N] [--note T]``
- ``usvc seller rooms invitations ROOM [--all]`` / ``revoke ROOM CODE_ID``
- ``usvc seller rooms join CODE`` / ``leave ROOM``

What the account may do is decided by the server from its role in the room.
"""

from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ._helpers import (
    api_key_option,
    async_client,
    base_url_option,
    model_to_dict,
    run_async,
)

console = Console()

app = typer.Typer(help="Rooms: list, read, post, settings, delivery and invitations.")


def _print_json(value: Any) -> None:
    console.print(json.dumps(value, indent=2, default=str))


def _rooms_table(rooms: list[dict[str, Any]]) -> None:
    table = Table(title="Rooms")
    for column, style in (("ID", "dim"), ("Kind", ""), ("Name", "bold"), ("Handle", ""), ("Role", ""), ("Status", "")):
        table.add_column(column, style=style or None)
    for room in rooms:
        table.add_row(
            str(room.get("id", "")),
            str(room.get("kind", "")),
            str(room.get("name", "")),
            str(room.get("handle", "")),
            str(room.get("role", "")),
            str(room.get("status", "")),
        )
    console.print(table)


@app.command("list")
def list_rooms(
    kind: str | None = typer.Option(None, "--kind", help="Only rooms of this kind (chat, me, helpdesk)."),
    enrollment: str | None = typer.Option(None, "--enrollment", help="Only rooms of this enrollment."),
    service: str | None = typer.Option(None, "--service", help="Only rooms of this service (not its enrollments')."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the rooms the account can reach, most recently active first."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            listed = await client.rooms.list(kind=kind, enrollment=enrollment, service=service)
            return [model_to_dict(room) for room in listed.data]

    rooms = run_async(_impl(), error_prefix="Failed to list rooms")
    if output_format == "json":
        _print_json(rooms)
    elif not rooms:
        console.print("[dim]No rooms found[/dim]")
    else:
        _rooms_table(rooms)


@app.command("show")
def show_room(
    room: str = typer.Argument(..., help="Room id or handle."),
    after: int | None = typer.Option(None, "--after", help="Resume after this offset (a previous page's next)."),
    limit: int = typer.Option(50, "--limit", help="Messages per page (at most 200)."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show a room and its messages, oldest first."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.get(room, after=after, limit=limit))

    view = run_async(_impl(), error_prefix="Failed to show room")
    if output_format == "json":
        _print_json(view)
        return
    console.print(f"[bold]{view.get('name', '')}[/bold]  ({view.get('kind', '')}, you are {view.get('role', '')})")
    if view.get("description"):
        console.print(view["description"])
    messages = (view.get("messages") or {}).get("data") or []
    for message in messages:
        console.print(
            f"[dim]{message.get('offset', '')} {message.get('sent_at', '')}[/dim] "
            f"[bold]{message.get('sender_name', '')}[/bold]: {message.get('body', '')}"
        )
    if not messages:
        console.print("[dim]No messages[/dim]")
    next_offset = (view.get("messages") or {}).get("next")
    if next_offset is not None:
        console.print(f"[dim]next: --after {next_offset}[/dim]")


@app.command("post")
def post_message(
    room: str = typer.Argument(..., help="Room id or handle."),
    text: str = typer.Argument(..., help="Message body."),
    title: str | None = typer.Option(None, "--title", help="Optional title."),
    client_message_id: str | None = typer.Option(
        None, "--id", help="Idempotency key: retrying with the same key posts once."
    ),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Post a message to a room."""
    message: dict[str, Any] = {}
    if title is not None:
        message["title"] = title
    if client_message_id is not None:
        message["client_message_id"] = client_message_id

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.post(room, body=text, **message))

    posted = run_async(_impl(), error_prefix="Failed to post")
    console.print(f"[green]✓[/green] Posted to {posted.get('room_id', room)} at offset {posted.get('offset', '')}")


@app.command("members")
def list_members(
    room: str = typer.Argument(..., help="Room id or handle."),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table | json."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the room's members and their roles."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            return [model_to_dict(m) for m in (await client.rooms.members(room)).data]

    members = run_async(_impl(), error_prefix="Failed to list members")
    if output_format == "json":
        _print_json(members)
        return
    table = Table(title="Members")
    for column in ("Name", "Account", "Role", "Joined"):
        table.add_column(column)
    for m in members:
        table.add_row(
            str(m.get("name", "")),
            str(m.get("account_type", "")),
            str(m.get("role", "")),
            str(m.get("joined_at", "")),
        )
    console.print(table)


@app.command("set")
def set_room(
    room: str = typer.Argument(..., help="Room id or handle."),
    name: str | None = typer.Option(None, "--name", help="New room name."),
    description: str | None = typer.Option(None, "--description", help="Markdown description; '' clears it."),
    retention: int | None = typer.Option(None, "--retention", help="Seconds to keep messages (0 = don't store)."),
    status: str | None = typer.Option(None, "--status", help="active | readonly (only owner and moderators post)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Change the room's settings (owner only)."""
    settings: dict[str, Any] = {
        key: value
        for key, value in (
            ("name", name),
            ("description", description),
            ("retention_seconds", retention),
            ("status", status),
        )
        if value is not None
    }
    if not settings:
        console.print("[yellow]Nothing to change[/yellow]")
        raise typer.Exit(code=1)

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.update(room, **settings))

    updated = run_async(_impl(), error_prefix="Failed to change the room")
    console.print(f"[green]✓[/green] Updated {updated.get('name', room)}")


@app.command("delivery")
def delivery(
    room: str = typer.Argument(..., help="Room id or handle."),
    notify: str | None = typer.Option(None, "--notify", help="auto | off | a notify service path."),
    email: str | None = typer.Option(None, "--email", help="auto | off | an email service path."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Show, or with --notify / --email change, how this room reaches you."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            if notify is None and email is None:
                return model_to_dict(await client.rooms.delivery(room))
            return model_to_dict(await client.rooms.set_delivery(room, notify=notify, email=email))

    _print_json(run_async(_impl(), error_prefix="Failed to read or change delivery"))


@app.command("invite")
def invite(
    room: str = typer.Argument(..., help="Room id or handle."),
    role: str = typer.Option("member", "--role", help="readonly | member | moderator."),
    max_uses: int | None = typer.Option(None, "--max-uses", help="Uses before the code stops working."),
    expires_in_days: int | None = typer.Option(None, "--expires-in-days", help="Defaults to 7 days."),
    note: str | None = typer.Option(None, "--note", help="A note for yourself."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Create an invitation code for the room."""
    options = {
        key: value
        for key, value in (("max_uses", max_uses), ("expires_in_days", expires_in_days), ("note", note))
        if value is not None
    }

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.create_invitation(room, role=role, **options))

    code = run_async(_impl(), error_prefix="Failed to create the invitation")
    console.print(f"[green]✓[/green] Invitation code [bold]{code.get('token', '')}[/bold] ({code.get('role', '')})")


@app.command("invitations")
def invitations(
    room: str = typer.Argument(..., help="Room id or handle."),
    include_inactive: bool = typer.Option(False, "--all", help="Include used-up, expired and revoked codes."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """List the room's invitation codes."""

    async def _impl() -> list[dict[str, Any]]:
        async with async_client(api_key, base_url) as client:
            listed = await client.rooms.invitations(room, include_inactive=include_inactive)
            return [model_to_dict(c) for c in listed.data]

    _print_json(run_async(_impl(), error_prefix="Failed to list invitations"))


@app.command("revoke")
def revoke(
    room: str = typer.Argument(..., help="Room id or handle."),
    code_id: str = typer.Argument(..., help="Invitation code id (from invitations)."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Revoke an invitation code."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.revoke_invitation(room, code_id))

    run_async(_impl(), error_prefix="Failed to revoke the invitation")
    console.print(f"[green]✓[/green] Revoked {code_id}")


@app.command("join")
def join(
    code: str = typer.Argument(..., help="Invitation code."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Join a room with an invitation code."""

    async def _impl() -> dict[str, Any]:
        async with async_client(api_key, base_url) as client:
            return model_to_dict(await client.rooms.join(code))

    joined = run_async(_impl(), error_prefix="Failed to join")
    console.print(f"[green]✓[/green] Joined {joined.get('name', '')} as @{joined.get('handle', '')}")


@app.command("leave")
def leave(
    room: str = typer.Argument(..., help="Room id or handle."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt."),
    api_key: str | None = api_key_option(),
    base_url: str = base_url_option(),
) -> None:
    """Leave a room you joined (chat rooms; the owner can't leave)."""
    if not yes and not typer.confirm(f"Leave room '{room}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        raise typer.Exit(code=0)

    async def _impl() -> None:
        async with async_client(api_key, base_url) as client:
            await client.rooms.leave(room)

    run_async(_impl(), error_prefix="Failed to leave")
    console.print(f"[green]✓[/green] Left {room}")
