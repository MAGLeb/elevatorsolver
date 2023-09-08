import random

import numpy as np

from core.types.action_type import ActionType
from core.solution.q_table_agent.utils import boolean_array_to_integer


class LearningAgentQTable:
    def __init__(self, levels, learning_rate=0.1, discount_rate=0.9, exploration_rate=1, exploration_fall=0.975):
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.exploration_fall = exploration_fall
        self.q_table = np.zeros((levels, 2 ** levels, 2 ** levels, 8, 5), dtype=np.int32)

    def save(self, filename):
        np.save(filename, self.q_table)

    def load(self, filename):
        self.q_table = np.load(filename)

    def reset_exploration_rate(self):
        self.exploration_rate = 1

    def choose_action(self, state) -> ActionType:
        self.exploration_rate *= self.exploration_fall
        random_action = random.random()
        if random_action < self.exploration_rate:
            return ActionType(random.randint(0, ActionType.__len__() - 1))
        outside_calls, inside_calls, current_level, weight = state
        outside_calls_int = boolean_array_to_integer(outside_calls)
        inside_calls_int = boolean_array_to_integer(inside_calls)
        best_action = np.argmax(self.q_table[current_level - 1, outside_calls_int, inside_calls_int, weight])
        return ActionType(best_action)

    def learn(self, state, reward, action: ActionType, next_state):
        outside_calls, inside_calls, current_level, weight = state
        outside_calls_int = boolean_array_to_integer(outside_calls)
        inside_calls_int = boolean_array_to_integer(inside_calls)

        next_outside_calls, next_inside_calls, next_current_level, next_weight = next_state
        next_outside_calls_int = boolean_array_to_integer(next_outside_calls)
        next_inside_calls_int = boolean_array_to_integer(next_inside_calls)

        action = action.value
        current_level -= 1
        next_current_level -= 1
        current_value = self.q_table[current_level, outside_calls_int, inside_calls_int, weight, action] * (
                1 - self.learning_rate)
        next_value = ((reward + self.discount_rate *
                       np.max(self.q_table[
                                  next_current_level, next_outside_calls_int, next_inside_calls_int, next_weight])) *
                      self.learning_rate)
        self.q_table[current_level, outside_calls_int, inside_calls_int, weight, action] = current_value + next_value
