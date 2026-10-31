"""Account-scoped rooms, messages, owner settings and invitation codes.

Room descriptions are Markdown. Read the returned retention/permanence fields
for current policy instead of deriving rules from description text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from ._generated.types import UNSET
from ._http import unwrap

if TYPE_CHECKING:
    from ._generated.client import AuthenticatedClient
    from ._generated.models.room_delivery import RoomDelivery
    from ._generated.models.room_invitation_code import RoomInvitationCode
    from ._generated.models.room_invitation_codes import RoomInvitationCodes
    from ._generated.models.room_list import RoomList
    from ._generated.models.room_members import RoomMembers
    from ._generated.models.room_post_response import RoomPostResponse
    from ._generated.models.room_summary import RoomSummary
    from ._generated.models.room_view import RoomView


class Rooms:
    """Room operations for the key's seller account (``client.rooms``)."""

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def list(self, *, kind: str | None = None) -> RoomList:
        """List the account's rooms, optionally filtered by kind."""
        from ._generated.api.seller_rooms import seller_rooms_list_rooms

        return unwrap(seller_rooms_list_rooms.sync_detailed(client=self._client, kind=UNSET if kind is None else kind))

    def get(self, target: str, *, after: int | None = None, limit: int = 50) -> RoomView:
        """Read a room by UUID or handle; resume history with the previous messages.next."""
        from ._generated.api.seller_rooms import seller_rooms_get_room_messages

        return unwrap(
            seller_rooms_get_room_messages.sync_detailed(
                target, client=self._client, after=UNSET if after is None else after, limit=limit
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
        """Update owner settings: name, Markdown description, retention_seconds, status
        (active, paused or readonly) or pause_message. Omitted fields are unchanged; null clears
        optional values.
        """
        from ._generated.api.seller_rooms import seller_rooms_update_room_settings
        from ._generated.models.room_settings_update import RoomSettingsUpdate

        return unwrap(
            seller_rooms_update_room_settings.sync_detailed(
                target, client=self._client, body=RoomSettingsUpdate.from_dict(settings)
            )
        )

    def post(self, target: str | None = None, *, body: str, **message: Any) -> RoomPostResponse:
        """Post a message in msg format. Target is a UUID or handle; None uses a leading @handle or the me
        fallback. Pass client_message_id for idempotent retries.
        """
        from ._generated.api.seller_rooms import seller_rooms_post_room_message
        from ._generated.models.room_post_request import RoomPostRequest

        if target is not None:
            from ._generated.api.seller_rooms import seller_rooms_post_room_message_to

            return unwrap(
                seller_rooms_post_room_message_to.sync_detailed(
                    target, client=self._client, body=RoomPostRequest.from_dict({"body": body, **message})
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
