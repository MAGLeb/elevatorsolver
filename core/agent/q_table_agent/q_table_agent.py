import random

import numpy as np

from core.agent.agent import Agent
from core.types.action_type import ActionType


class LearningAgentQTable(Agent):
    def __init__(self, learning_rate=0.1, discount_rate=0.9, exploration_rate=1):
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.q_table = np.zeros((self.levels, 2 ** self.levels, 2 ** self.levels, 8, 2, 5), dtype=np.int32)

    def save(self, filepath):
        np.save(filepath, self.q_table)

    def load(self, filepath):
        self.q_table = np.load(filepath)

    def reset_exploration_rate(self):
        self.exploration_rate = 1

    def choose_action(self, state) -> ActionType:
        self.exploration_rate *= self.exploration_fall
        random_action = random.random()
        if random_action < self.exploration_rate:
            return random.choice(list(ActionType))
        outside_calls, inside_calls, current_level, weight, is_opened = state
        outside_calls_int = self.boolean_array_to_integer(outside_calls)
        inside_calls_int = self.boolean_array_to_integer(inside_calls)
        best_action = np.argmax(self.q_table[current_level - 1, outside_calls_int, inside_calls_int, weight, is_opened])
        return ActionType(best_action)

    def learn(self, state, reward, action: ActionType, next_state):
        outside_calls, inside_calls, current_level, weight, is_opened = state
        outside_calls_int = self.boolean_array_to_integer(outside_calls)
        inside_calls_int = self.boolean_array_to_integer(inside_calls)

        next_outside_calls, next_inside_calls, next_current_level, next_weight, next_is_opened = next_state
        next_outside_calls_int = self.boolean_array_to_integer(next_outside_calls)
        next_inside_calls_int = self.boolean_array_to_integer(next_inside_calls)

        action = action.value
        current_level -= 1
        next_current_level -= 1
        current_value = self.q_table[current_level, outside_calls_int, inside_calls_int, weight, is_opened, action] * (
                1 - self.learning_rate)
        next_value = ((reward + self.discount_rate *
                       np.max(self.q_table[
                                  next_current_level, next_outside_calls_int, next_inside_calls_int,
                                  next_weight, next_is_opened])) * self.learning_rate)
        self.q_table[
            current_level, outside_calls_int, inside_calls_int, weight, is_opened, action] = current_value + next_value

    @staticmethod
    def boolean_array_to_integer(a):
        return int(''.join(map(str, a)), 2)