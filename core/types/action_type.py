from enum import Enum


class ActionType(Enum):
    EMPTY = -1
    UP = 0
    DOWN = 1
    CLOSE_DOOR = 2
    OPEN_DOOR = 3
    WAIT = 4
