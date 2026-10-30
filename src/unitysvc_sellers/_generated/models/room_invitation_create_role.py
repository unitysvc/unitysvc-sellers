from typing import Literal, cast

RoomInvitationCreateRole = Literal["member", "moderator", "readonly"]

ROOM_INVITATION_CREATE_ROLE_VALUES: set[RoomInvitationCreateRole] = {
    "member",
    "moderator",
    "readonly",
}


def check_room_invitation_create_role(value: str) -> RoomInvitationCreateRole:
    if value in ROOM_INVITATION_CREATE_ROLE_VALUES:
        return cast(RoomInvitationCreateRole, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ROOM_INVITATION_CREATE_ROLE_VALUES!r}")
