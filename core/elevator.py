from core.action_type import ActionType
from core.level_type import LevelType
from core.reward_type import RewardType


class Elevator:
    def __init__(self, levels):
        self.levels = levels
        self.calls = [LevelType.EMPTY] * levels

        self.time_to_move_between_level = 2
        self.time_to_open_close_door = 3

        self.current_level = 1
        self.is_door_open = False
        self.in_action = False

    def step(self, action: ActionType):
        reward = 0
        if action == 0:
            if self.is_door_open:
                reward -= RewardType.MOVE_WITH_OPEN_DOOR
            self.current_level += 1
            reward += RewardType.MOVE_BETWEEN_LEVELS

        elif action == 1:
            if self.is_door_open:
                reward -= RewardType.MOVE_WITH_OPEN_DOOR
            self.current_level -= 1
            reward += RewardType.MOVE_BETWEEN_LEVELS

        elif action == 2:
            if self.is_door_open:
                reward += RewardType.CLOSE_DOOR
            reward += RewardType.OPEN_CLOSE_DOOR
            self.is_door_open = False

        elif action == 3:
            reward += RewardType.OPEN_CLOSE_DOOR
            self.is_door_open = True

            if self.calls[self.current_level] == LevelType.GET_PASSENGER:
                self.calls[self.current_level] = LevelType.EMPTY
                reward += RewardType.GET_PASSENGER
            elif self.calls[self.current_level] == LevelType.OUT_PASSENGER:
                self.calls[self.current_level] = LevelType.EMPTY
                reward += RewardType.DELIVER_PASSENGER
            else:
                reward += RewardType.OPEN_ON_EMPTY_LEVEL

        elif action == 4:
            if self.calls.count(LevelType.EMPTY) == self.levels:
                reward += RewardType.WAIT_WHEN_NO_CALLS
            else:
                reward += RewardType.WAIT_WHEN_CALLS

        return self.get_state(), reward

    def add_calls(self, level, level_type: LevelType):
        self.calls[level - 1] = level_type

    def get_state(self):
        return self.calls, self.current_level, self.in_action


