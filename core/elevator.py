from typing import List

from core.types.action_type import ActionType
from core.types.reward_type import RewardType
from core.level import Level


class StateElevator:
    def __init__(self, going_to_level: List[int], current_level: int, current_weight: int, max_weight: int, is_open_door: int):
        self.going_to_level = going_to_level
        self.current_level = current_level
        self.current_weight = current_weight
        self.max_weight = max_weight
        self.is_open_door = is_open_door


class Elevator:
    def __init__(self, max_levels: int, max_weight: int):
        self.max_levels = max_levels
        self.max_weight = max_weight

        self.passengers = []
        self.going_to_level = [0 for _ in range(max_levels)]
        self.current_weight = 0
        self.current_level = 0
        self.is_door_open = False

    def step(self, action: ActionType, levels: List[Level]) -> int:
        if action == ActionType.UP:
            reward = self._up()
        elif action == ActionType.DOWN:
            reward = self._down()
        elif action == ActionType.CLOSE_DOOR:
            reward = self._close()
        elif action == ActionType.OPEN_DOOR:
            reward = self._open(levels)
        elif action == ActionType.WAIT:
            reward = 0
        else:
            raise ValueError("Only 5 types of action.")

        return reward

    def _get_passengers_into_elevator(self, levels: List[Level]) -> int:
        passengers = 0
        level = levels[self.current_level]

        while level.get_passenger() is not None:
            if self.max_weight < self.current_weight + level.get_passenger().weight:
                break
            passenger = level.pop_passenger()
            self.current_weight += passenger.weight
            number_level = passenger.to_level
            self.going_to_level[number_level] = 1
            passengers += 1

        return passengers * RewardType.GET_PASSENGER.value

    def _get_out_passengers_from_elevator(self) -> int:
        reward = 0

        for p in self.passengers:
            if p.to_level == self.current_level:
                self.current_weight -= p.weight
                reward += RewardType.DELIVER_PASSENGER.value
        self.passengers = [p for p in self.passengers if p.to_level != self.current_level]

        return reward

    def get_state(self) -> StateElevator:
        state = StateElevator(self.going_to_level, self.current_level,
                              self.current_weight, self.max_weight, self.is_door_open)
        return state

    def _up(self):
        reward = RewardType.UP_DOWN_STEP.value

        if self.is_door_open:
            reward -= RewardType.MOVE_WITH_OPEN_DOOR.value

        if self.current_level == self.max_levels - 1:
            reward -= RewardType.MOVE_NEXT_TO_EDGE.value
        else:
            self.current_level += 1
        return reward

    def _down(self):
        reward = RewardType.UP_DOWN_STEP.value

        if self.is_door_open:
            reward -= RewardType.MOVE_WITH_OPEN_DOOR.value

        if self.current_level == 0:
            reward -= RewardType.MOVE_NEXT_TO_EDGE.value
        else:
            self.current_level -= 1
        return reward

    def _close(self):
        reward = RewardType.OPEN_CLOSE_DOOR.value
        self.is_door_open = False
        return reward

    def _open(self, levels: List[Level]):
        self.going_to_level[self.current_level] = 0
        self.is_door_open = True

        reward = RewardType.OPEN_CLOSE_DOOR.value
        # 1. get out passengers from elevator
        reward += self._get_out_passengers_from_elevator()
        # 2. enter passengers to elevator
        reward += self._get_passengers_into_elevator(levels)

        return reward
