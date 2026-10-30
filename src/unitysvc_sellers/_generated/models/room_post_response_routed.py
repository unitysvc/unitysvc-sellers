from typing import Literal, cast

RoomPostResponseRouted = Literal["handle", "me", "room_id"]

ROOM_POST_RESPONSE_ROUTED_VALUES: set[RoomPostResponseRouted] = {
    "handle",
    "me",
    "room_id",
}


def check_room_post_response_routed(value: str) -> RoomPostResponseRouted:
    if value in ROOM_POST_RESPONSE_ROUTED_VALUES:
        return cast(RoomPostResponseRouted, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ROOM_POST_RESPONSE_ROUTED_VALUES!r}")
