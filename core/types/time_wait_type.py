from enum import Enum

from core.action_type import ActionType


class TimeWaitType(Enum):
    MOVE_BETWEEN_LEVEL = 2
    OPEN_CLOSE_DOOR = 3
    WAIT = 0

    @classmethod
    def get_time_to_wait(cls, action_type: ActionType):
        if action_type in [ActionType.CLOSE_DOOR, ActionType.OPEN_DOOR]:
            return cls.OPEN_CLOSE_DOOR
        elif action_type in [ActionType.UP, ActionType.DOWN]:
            return cls.MOVE_BETWEEN_LEVEL
        elif action_type == ActionType.WAIT:
            return cls.WAIT
