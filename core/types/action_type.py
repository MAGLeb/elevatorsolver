from enum import Enum


class ActionType(Enum):
    UP = 0
    DOWN = 1
    WAIT = 2
    STOP = 3  # остановиться и обслужить этаж (открыть двери)
