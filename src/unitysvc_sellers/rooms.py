"""Account-scoped rooms, messages, owner settings and invitation codes.

Room descriptions are Markdown. Read the returned retention fields for current
policy instead of deriving rules from description text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET
from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.room_active_response import RoomActiveResponse
    from ._generated.models.room_delivery import RoomDelivery
    from ._generated.models.room_feed import RoomFeed
    from ._generated.models.room_follow_up import RoomFollowUp
    from ._generated.models.room_invitation_code import RoomInvitationCode
    from ._generated.models.room_invitation_codes import RoomInvitationCodes
    from ._generated.models.room_list import RoomList
    from ._generated.models.room_members import RoomMembers
    from ._generated.models.room_post_response import RoomPostResponse
    from ._generated.models.room_summary import RoomSummary
    from ._generated.models.room_unread import RoomUnread
    from ._generated.models.room_view import RoomView


def _id(value: Any) -> Any:
    """An id from an id or an SDK object carrying ``.id``; UNSET for None."""
    if value is None:
        return UNSET
    raw = getattr(value, "id", value)
    return raw if isinstance(raw, UUID) else UUID(str(raw))


class Rooms:
    """Room operations for the key's seller account (``client.rooms``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(
        self,
        *,
        kind: str | None = None,
        enrollment: Any = None,
        service: Any = None,
        q: str | None = None,
        new_activity: bool = False,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> RoomList:
        """List the rooms the account can reach, most recently active first,
        narrowed by kind, enrollment, service, a case-insensitive name prefix
        (``q``) or unseen activity (``new_activity``). ``enrollment`` /
        ``service`` take an id or the SDK object; each matches that exact
        scope (a service's rooms, not its enrollments'). Without ``limit``
        every room is returned; with it, pass the result's ``next_cursor`` as
        ``cursor`` for the next page. Each row carries ``can_post`` (for this
        key) and ``last_sender_name``."""
        from ._generated.api.seller_rooms import seller_rooms_list_rooms

        return unwrap(
            seller_rooms_list_rooms.sync_detailed(
                client=self._client,
                kind=UNSET if kind is None else kind,
                enrollment=_id(enrollment),
                service=_id(service),
                q=UNSET if q is None else q,
                new_activity=new_activity or UNSET,
                limit=UNSET if limit is None else limit,
                cursor=UNSET if cursor is None else cursor,
            )
        )

    def feed(
        self,
        *,
        since: str | None = None,
        wait: float = 0,
        limit: int = 100,
        rooms: Any = None,
    ) -> RoomFeed:
        """New messages across the account's rooms, each tagged with ``room_id``.

        Omit ``since`` to start at the current end (no backlog); pass the
        result's ``cursor`` as ``since`` to get only what came after it.
        ``wait`` (at most 25 s) long-polls until a message is stored; keep it
        below the client's timeout (30 s by default). ``rooms`` narrows the
        feed to some room ids (or SDK objects). An invalid ``since`` raises
        ValidationError: start again without it."""
        from ._generated.api.seller_rooms import seller_rooms_room_feed

        return unwrap(
            seller_rooms_room_feed.sync_detailed(
                client=self._client,
                since=UNSET if since is None else since,
                wait=wait,
                limit=limit,
                room=UNSET if rooms is None else [_id(room) for room in rooms],
            )
        )

    def leave(self, target: str) -> None:
        """Leave a room the account joined, if its kind allows it (a chat room).
        The owner can't leave, and a membership that comes from an enrollment
        follows the enrollment instead."""
        from ._generated.api.seller_rooms import seller_rooms_leave_room

        unwrap(seller_rooms_leave_room.sync_detailed(target, client=self._client))

    def get(
        self,
        target: str,
        *,
        after: int | None = None,
        limit: int = 50,
        tail: int | None = None,
        before: int | None = None,
    ) -> RoomView:
        """Read a room by UUID or handle; resume history with the previous messages.next.
        ``tail`` (instead of ``after``) reads the latest N messages, still oldest first;
        their ``next`` resumes with newer messages only, and ``messages.previous``
        (null when nothing older is stored) reads the page before them with
        ``tail=N, before=previous``."""
        from ._generated.api.seller_rooms import seller_rooms_get_room_messages

        return unwrap(
            seller_rooms_get_room_messages.sync_detailed(
                target,
                client=self._client,
                after=UNSET if after is None else after,
                limit=limit,
                tail=UNSET if tail is None else tail,
                before=UNSET if before is None else before,
            )
        )

    def unread(self) -> RoomUnread:
        """How many of the account's rooms have activity it hasn't seen."""
        from ._generated.api.seller_rooms import seller_rooms_count_unread_rooms

        return unwrap(seller_rooms_count_unread_rooms.sync_detailed(client=self._client))

    def mark_active(self, target: str, offset: int) -> RoomActiveResponse:
        """Record that the account has seen the room through ``offset`` (a message's offset).
        Call it when a person opens a room and when they stop viewing it; reading
        history records nothing. ``capped`` means storage hasn't reached ``offset`` yet."""
        from ._generated.api.seller_rooms import seller_rooms_mark_room_active
        from ._generated.models.room_active_request import RoomActiveRequest

        return unwrap(
            seller_rooms_mark_room_active.sync_detailed(
                target, client=self._client, body=RoomActiveRequest(offset=offset)
            )
        )

    def set_follow_up(self, target: str, follow_up: bool = True) -> RoomFollowUp:
        """Flag the room for this account to revisit, or clear the flag."""
        from ._generated.api.seller_rooms import seller_rooms_set_room_follow_up
        from ._generated.models.room_follow_up import RoomFollowUp

        return unwrap(
            seller_rooms_set_room_follow_up.sync_detailed(
                target, client=self._client, body=RoomFollowUp(follow_up=follow_up)
            )
        )

    def members(self, target: str) -> RoomMembers:
        """List active member accounts without their private delivery settings."""
        from ._generated.api.seller_rooms import seller_rooms_list_room_members

        return unwrap(seller_rooms_list_room_members.sync_detailed(target, client=self._client))

    def delivery(self, target: str) -> RoomDelivery:
        """Read this account's notify/email delivery paths and whether they can be edited."""
        from ._generated.api.seller_rooms import seller_rooms_get_room_delivery

        return unwrap(seller_rooms_get_room_delivery.sync_detailed(target, client=self._client))

    def set_delivery(self, target: str, *, notify: str | None = None, email: str | None = None) -> RoomDelivery:
        """Set notify/email to auto, off or a delivery path. Omitted channels stay unchanged."""
        from ._generated.api.seller_rooms import seller_rooms_update_room_delivery
        from ._generated.models.room_delivery_update import RoomDeliveryUpdate

        settings = {name: value for name, value in {"notify": notify, "email": email}.items() if value is not None}
        return unwrap(
            seller_rooms_update_room_delivery.sync_detailed(
                target, client=self._client, body=RoomDeliveryUpdate.from_dict(settings)
            )
        )

    def update(self, target: str, **settings: Any) -> RoomSummary:
        """Update owner settings: name, Markdown description, retention_seconds or status
        (active or readonly). Omitted fields are unchanged; null clears optional values.
        """
        from ._generated.api.seller_rooms import seller_rooms_update_room_settings
        from ._generated.models.room_settings_update import RoomSettingsUpdate

        return unwrap(
            seller_rooms_update_room_settings.sync_detailed(
                target, client=self._client, body=RoomSettingsUpdate.from_dict(settings)
            )
        )

    def post(
        self,
        target: str | None = None,
        *,
        body: str = "",
        attachments: Any = None,
        fallback: bool = True,
        **message: Any,
    ) -> RoomPostResponse:
        """Post a message in msg format. Target is a UUID or handle; None uses a leading @handle or the me
        fallback. With a target and ``fallback=False``, a room that can't take the post raises
        (NotFoundError / PermissionError) instead of posting to ``me``. Pass client_message_id for
        idempotent retries.

        ``attachments`` takes file paths, ``http(s)`` URLs (kept as links) or entries from
        :mod:`unitysvc.attachments`; files are stored for 7 days. A message needs a ``body`` or a
        file (a URL alone needs a ``body``): otherwise ValueError, before anything is sent.
        """
        if attachments:
            from unitysvc.attachments import check_content, prepare

            message["attachments"] = prepare(attachments)
            check_content(body, message["attachments"])
        from ._generated.api.seller_rooms import seller_rooms_post_room_message
        from ._generated.models.room_post_request import RoomPostRequest

        if target is not None:
            from ._generated.api.seller_rooms import seller_rooms_post_room_message_to

            return unwrap(
                seller_rooms_post_room_message_to.sync_detailed(
                    target,
                    client=self._client,
                    body=RoomPostRequest.from_dict({"body": body, **message}),
                    fallback=fallback,
                )
            )

        return unwrap(
            seller_rooms_post_room_message.sync_detailed(
                client=self._client, body=RoomPostRequest.from_dict({"body": body, **message})
            )
        )

    def join(self, token: str) -> RoomSummary:
        """Redeem an invitation as this account; already-member joins preserve its role."""
        from ._generated.api.seller_rooms import seller_rooms_join_room
        from ._generated.models.room_join_request import RoomJoinRequest

        return unwrap(seller_rooms_join_room.sync_detailed(client=self._client, body=RoomJoinRequest(token=token)))

    def invitations(self, target: str, *, include_inactive: bool = False) -> RoomInvitationCodes:
        """List invitation codes the caller is authorized to manage."""
        from ._generated.api.seller_rooms import seller_rooms_list_room_invitation_codes

        return unwrap(
            seller_rooms_list_room_invitation_codes.sync_detailed(
                target, client=self._client, include_inactive=include_inactive
            )
        )

    def create_invitation(self, target: str, *, role: str = "member", **options: Any) -> RoomInvitationCode:
        """Create an invitation. Options: expires_in_days, max_uses and note; the server enforces the inviter
        role cap.
        """
        from ._generated.api.seller_rooms import seller_rooms_create_room_invitation_code
        from ._generated.models.room_invitation_create import RoomInvitationCreate

        return unwrap(
            seller_rooms_create_room_invitation_code.sync_detailed(
                target, client=self._client, body=RoomInvitationCreate.from_dict({"role": role, **options})
            )
        )

    def revoke_invitation(self, target: str, code_id: str | UUID) -> RoomInvitationCode:
        """Revoke a code for future joins; existing memberships are preserved."""
        from ._generated.api.seller_rooms import seller_rooms_revoke_room_invitation_code

        return unwrap(
            seller_rooms_revoke_room_invitation_code.sync_detailed(target, UUID(str(code_id)), client=self._client)
        )
