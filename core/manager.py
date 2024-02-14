from typing import List

from core.level import Level
from core.elevator import Elevator
from core.utils.elevator_info import ElevatorInfo
from core.types.action_type import ActionType


class Manager:
    def __init__(self, max_levels: int, elevators_info: List[ElevatorInfo]):
        self.elevators = [Elevator(max_levels, elevators_info[i].max_weight) for i in range(len(elevators_info))]
        self.max_levels = max_levels
        self.levels = [Level(i) for i in range(self.max_levels)]

    def step(self, actions: List[ActionType]) -> int:
        reward = 0
        for i, elevator in enumerate(self.elevators):
            action = actions[i]
            reward += elevator.step(action, self.levels)

        return reward
