from typing import Literal, cast

RoomInvitationUpdateRoleType0 = Literal["member", "moderator", "readonly"]

ROOM_INVITATION_UPDATE_ROLE_TYPE_0_VALUES: set[RoomInvitationUpdateRoleType0] = {
    "member",
    "moderator",
    "readonly",
}


def check_room_invitation_update_role_type_0(value: str) -> RoomInvitationUpdateRoleType0:
    if value in ROOM_INVITATION_UPDATE_ROLE_TYPE_0_VALUES:
        return cast(RoomInvitationUpdateRoleType0, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ROOM_INVITATION_UPDATE_ROLE_TYPE_0_VALUES!r}")
