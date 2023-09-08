from typing import Optional

from core.level import Level
from core.types.action_type import ActionType
from core.types.reward_type import RewardType
from core.passenger import Passenger


class Elevator:
    def __init__(self, levels, max_weight):
        self.max_levels = levels
        self.max_weight = max_weight
        self.levels = [Level(i) for i in range(levels + 1)]
        self.passengers = []

        self.weight = 0
        self.current_level = 1
        self.is_door_open = False

    def step(self, action: ActionType):
        if action == ActionType.UP:
            reward = self._up()
        elif action == ActionType.DOWN:
            reward = self._down()
        elif action == ActionType.CLOSE_DOOR:
            reward = self._close()
        elif action == ActionType.OPEN_DOOR:
            reward = self._open()
        elif action == ActionType.WAIT:
            reward = self._wait()
        else:
            raise ValueError("Only 5 types of action.")
        state = self.get_state()
        reward -= sum(state[0]) * RewardType.PASSENGER_WAIT.value
        reward -= sum(state[1]) * RewardType.PASSENGER_WAIT.value
        return state, reward

    def get_passengers_into_elevator(self, level: Level):
        passengers = 0
        while level.passengers:
            if self.max_weight < self.weight + level.passengers[0].weight:
                break
            p = level.passengers.pop(0)
            self.passengers.append(p)
            self.weight += p.weight
            self.add_call(p.to_level, True, None)
            passengers += 1

        if level.is_empty():
            level.type = [0, 0]
        else:
            level.type = [1, 0]
        return passengers

    def add_call(self, level, is_inside_call: bool, passenger: Optional[Passenger]):
        if is_inside_call:
            self.levels[level].set_inside_elevator_call()
        else:
            self.levels[level].set_outside_elevator_call(passenger)

    def get_state(self):
        outside_calls = [level.type[0] for level in self.levels]
        inside_calls = [level.type[1] for level in self.levels]
        is_opened = 1 if self.is_door_open else 0
        return outside_calls, inside_calls, self.current_level, self.get_weight_state(), is_opened

    def get_weight_state(self):
        return min(7, int((self.weight * 8 / self.max_weight)))

    def _up(self):
        reward = 0
        if self.is_door_open:
            reward -= RewardType.MOVE_WITH_OPEN_DOOR.value

        if self.current_level == self.max_levels:
            reward -= RewardType.MOVE_NEXT_TO_EDGE.value
        else:
            self.current_level += 1
        return reward

    def _down(self):
        reward = 0
        if self.is_door_open:
            reward -= RewardType.MOVE_WITH_OPEN_DOOR.value

        if self.current_level == 1:
            reward -= RewardType.MOVE_NEXT_TO_EDGE.value
        else:
            self.current_level -= 1
        return reward

    def _close(self):
        reward = 0
        if self.is_door_open:
            reward += RewardType.CLOSE_DOOR.value
        self.is_door_open = False
        return reward

    def _open(self):
        reward = 0

        # 1. left passengers
        for p in self.passengers:
            if p.to_level == self.current_level:
                self.weight -= p.weight
                reward += RewardType.DELIVER_PASSENGER.value
        self.passengers = [p for p in self.passengers if p.to_level != self.current_level]

        # 2. enter passengers
        level = self.levels[self.current_level]
        number_new_passengers = self.get_passengers_into_elevator(level)
        reward += number_new_passengers * RewardType.GET_PASSENGER.value

        # 3. negative reward
        if reward == 0:
            if self.is_door_open:
                reward -= RewardType.OPEN_ON_EMPTY_LEVEL.value
            reward -= RewardType.OPEN_ON_EMPTY_LEVEL.value
        self.is_door_open = True

        return reward

    def _wait(self):
        reward = 0
        empty_levels = [level for level in self.levels if level.is_empty()]
        if len(empty_levels) == self.max_levels + 1:
            reward += RewardType.WAIT_WHEN_NO_CALLS.value
        else:
            reward -= RewardType.WAIT_WHEN_CALLS.value
        return reward
