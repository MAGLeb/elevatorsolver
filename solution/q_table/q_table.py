import random

import numpy as np

from core.action_type import ActionType
from solution.q_table.utils import boolean_array_to_integer


class LearningAgentQTable:
    def __init__(self, levels, learning_rate=0.1, discount_rate=0.9, exploration_rate=1, exploration_fall=0.999):
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.exploration_fall = exploration_fall
        self.q_table = np.zeroes((levels, 2 ** levels, 5))

    def save(self):
        pass

    def load(self):
        pass

    def choose_action(self, state) -> ActionType:
        random_action = random.random()
        if random_action < self.exploration_rate:
            return ActionType(random.randint(0, ActionType.__len__() - 1))
        calls, current_level, _ = state
        calls_int = boolean_array_to_integer(calls)
        best_action = np.argmax(self.q_table[current_level, calls_int])
        self.exploration_rate *= self.exploration_fall
        return ActionType(best_action)

    def learn(self, state, reward, action, next_state):
        # TODO in_action -> pass action
        calls, current_level, in_action = state
        calls_int = boolean_array_to_integer(calls)

        next_calls, next_current_level, next_in_action = next_state
        next_calls_int = boolean_array_to_integer(next_calls)

        current_value = self.q_table[current_level, calls_int, action] * (1 - self.learning_rate)
        next_value = ((reward + self.discount_rate * np.max(self.q_table[next_current_level, next_calls_int])) *
                      self.learning_rate)
        self.q_table[current_level, calls_int, action] = current_value + next_value
        # TODO finish write method
