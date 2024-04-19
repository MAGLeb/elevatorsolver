from enum import Enum


class RewardType(Enum):
    GET_PASSENGER = 0.5
    DELIVER_PASSENGER = 0.5

    OPEN_CLOSE_DOOR = -0.005
    UP_DOWN_STEP = -0.015
    PASSENGER_WAIT = -0.05
    MOVE_NEXT_TO_EDGE = -1
    MOVE_WITH_OPEN_DOOR = -1

    @classmethod
    def to_string(cls):
        return "; ".join(f"{name.replace('_', ' ')}: {value.value}" for name, value in cls.__members__.items())
