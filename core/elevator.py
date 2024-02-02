from typing import List

from core.types.action_type import ActionType
from core.types.reward_type import RewardType
from core.level import Level


class Elevator:
    def __init__(self, max_levels: int, max_weight: int):
        self.max_levels = max_levels
        self.max_weight = max_weight
        self.passengers = []
        self.going_to_level = []

        self.current_weight = 0
        self.current_level = 0
        self.is_door_open = False

    def step(self, action: ActionType, levels: List[Level]):
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
        state = self.get_state()

        return state, reward

    def get_passengers_into_elevator(self, levels: List[Level]) -> int:
        passengers = 0
        level = levels[self.current_level]

        while not level.is_empty():
            if self.max_weight < self.current_weight + level.get_passenger().weight:
                break
            passenger = level.pop_passenger()
            self.current_weight += passenger.weight
            number_level = passenger.to_level
            levels[number_level].set_inside_elevator_call()
            passengers += 1

        level.update_status_call()
        return passengers

    def get_state(self):
        is_opened = 1 if self.is_door_open else 0
        return self.going_to_level, self.current_level, self._weight_converter(), is_opened

    def _weight_converter(self):
        # Map from wide space to [0, 1] range output. It is help NN learn better.
        return self.current_weight / self.max_weight

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
        reward = RewardType.OPEN_CLOSE_DOOR.value

        for p in self.passengers:
            if p.to_level == self.current_level:
                self.current_weight -= p.weight
                reward += RewardType.DELIVER_PASSENGER.value
        self.passengers = [p for p in self.passengers if p.to_level != self.current_level]

        # 2. enter passengers
        number_new_passengers = self.get_passengers_into_elevator(levels)
        reward += number_new_passengers * RewardType.GET_PASSENGER.value

        self.is_door_open = True

        return reward
