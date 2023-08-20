from core.level import Level
from core.types.action_type import ActionType
from core.types.level_type import LevelType
from core.types.reward_type import RewardType
from core.passenger import Passenger


class Elevator:
    def __init__(self, levels):
        self.levels = levels
        self.calls = [Level(i) for i in range(levels + 1)]
        self.passengers = []

        self.weight = 0
        self.current_level = 0
        self.is_door_open = False

    def step(self, action: ActionType):
        reward = 0
        if action == 0:
            if self.is_door_open:
                reward -= RewardType.MOVE_WITH_OPEN_DOOR

            if self.current_level == self.levels:
                reward -= RewardType.MOVE_NEXT_TO_EDGE
            else:
                self.current_level += 1
                reward -= RewardType.MOVE_BETWEEN_LEVELS

        elif action == 1:
            if self.is_door_open:
                reward -= RewardType.MOVE_WITH_OPEN_DOOR

            if self.current_level == 0:
                reward -= RewardType.MOVE_NEXT_TO_EDGE
            else:
                self.current_level -= 1
                reward -= RewardType.MOVE_BETWEEN_LEVELS

        elif action == 2:
            if self.is_door_open:
                reward += RewardType.CLOSE_DOOR
            reward -= RewardType.OPEN_CLOSE_DOOR
            self.is_door_open = False

        elif action == 3:
            if not self.calls[self.current_level].is_empty():
                number_passengers = self.calls[self.current_level].get_passengers_into_elevator()
                reward += RewardType.GET_PASSENGER * number_passengers
            elif self.calls[self.current_level] == LevelType.CALLED:
                self.outside_calls[self.current_level] = LevelType.EMPTY
                reward += RewardType.DELIVER_PASSENGER
            else:
                reward -= RewardType.OPEN_ON_EMPTY_LEVEL
            reward -= RewardType.OPEN_CLOSE_DOOR
            self.is_door_open = True

        elif action == 4:
            if self.calls.count(LevelType.EMPTY) == self.levels:
                reward += RewardType.WAIT_WHEN_NO_CALLS
            else:
                reward -= RewardType.WAIT_WHEN_CALLS

        return self.get_state(), reward

    def add_call(self, level, passenger: Passenger):
        self.calls[level].set_outside_call(passenger)

    def get_state(self):
        return self.inside_calls, self.outside_calls, self.current_level


