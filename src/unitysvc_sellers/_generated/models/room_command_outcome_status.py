from typing import Literal, cast

RoomCommandOutcomeStatus = Literal["executed", "not_recognized", "refused"]

ROOM_COMMAND_OUTCOME_STATUS_VALUES: set[RoomCommandOutcomeStatus] = {
    "executed",
    "not_recognized",
    "refused",
}


def check_room_command_outcome_status(value: str) -> RoomCommandOutcomeStatus:
    if value in ROOM_COMMAND_OUTCOME_STATUS_VALUES:
        return cast(RoomCommandOutcomeStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ROOM_COMMAND_OUTCOME_STATUS_VALUES!r}")
