import random
from typing import List

import numpy as np

from core.agent.agent import Agent
from core.types.action_type import ActionType
from core.utils.environment import Environment


# ============================================================================
# DEPRECATED: Q-Table агент НЕ РАБОТАЕТ для задачи управления лифтом
# ============================================================================
# После серии экспериментов установлено:
# - Q-Table переобучается: Train +431, Validation -720
# - Пространство состояний слишком большое (409K для 5 этажей)
# - Даже reward shaping не помогает
#
# РЕКОМЕНДАЦИЯ: Используйте Base Agent (эвристика) или DQL (нейросеть)
# ============================================================================
#
# LEGACY CODE WARNING:
# This class, LearningAgentQTable, was originally designed to handle a single elevator only.
# It requires a specific state format: (outside_calls, inside_calls, current_level, weight, is_opened)
# Currently NOT compatible with multi-elevator configuration.
# Use only with: elevators=1, levels<=7 (memory constraint: 3.2GB at levels=10)
class LearningAgentQTable(Agent):
    def __init__(self):
        Agent.__init__(self)

        import warnings
        warnings.warn(
            "Q-Table агент DEPRECATED: не работает для задачи лифта. "
            "Используйте Base Agent или DQL.",
            DeprecationWarning
        )

        if self.elevators > 1:
            raise ValueError("LearningAgentQTable supports only 1 elevator. Use DQL for multi-elevator.")

        # Load hyperparameters from config
        self.learning_rate = Environment.Q_LEARNING_RATE
        self.discount_rate = Environment.Q_DISCOUNT_RATE
        self.exploration_rate = Environment.Q_EXPLORATION_RATE
        # Override exploration_fall if configured
        if Environment.Q_EXPLORATION_FALL is not None:
            self.exploration_fall = Environment.Q_EXPLORATION_FALL

        # Q-Table: [level, outside_calls, inside_calls, weight, door, action]
        # Memory: levels * 2^levels * 2^levels * 8 * 2 * 5 * 4 bytes
        # Optimistic initialization - encourages exploration of unknown states
        self.q_table = np.full((self.levels, 2 ** self.levels, 2 ** self.levels, 8, 2, 5), 0.5, dtype=np.float32)
        self._last_state_tuple = None
        self._initial_exploration_rate = self.exploration_rate

        print(f"Q-Table initialized: α={self.learning_rate}, γ={self.discount_rate}, ε={self.exploration_rate}")

    def save(self, filepath):
        np.save(filepath, self.q_table)

    def load(self, filepath):
        self.q_table = np.load(filepath)

    def _extract_state_tuple(self, manager_state):
        """Extract Q-Table state tuple from manager_state"""
        elevator_state = manager_state.elevators_state[0]
        outside_calls = [int(x) for x in manager_state.outside_calls]
        inside_calls = elevator_state.going_to_level
        current_level = elevator_state.current_level
        weight = min(int(elevator_state.current_weight / elevator_state.max_weight * 7), 7)
        is_opened = int(elevator_state.is_open_door)
        return (outside_calls, inside_calls, current_level, weight, is_opened)

    def choose_action(self, state, manager_state=None) -> List[ActionType]:
        self.exploration_rate *= self.exploration_fall

        if manager_state is None:
            return [random.choice(list(ActionType))]

        # Store state for learn()
        self._last_state_tuple = self._extract_state_tuple(manager_state)
        outside_calls, inside_calls, current_level, weight, is_opened = self._last_state_tuple

        # Exploration
        if random.random() < self.exploration_rate:
            return [random.choice(list(ActionType))]

        # Exploitation
        outside_calls_int = self.boolean_array_to_integer(outside_calls)
        inside_calls_int = self.boolean_array_to_integer(inside_calls)
        best_action = np.argmax(self.q_table[current_level, outside_calls_int, inside_calls_int, weight, is_opened])
        return [ActionType(best_action)]

    def learn(self, state, reward, action, next_state, case_info=None, manager_state=None, next_manager_state=None):
        if manager_state is None or next_manager_state is None:
            return

        # Extract state tuples
        outside_calls, inside_calls, current_level, weight, is_opened = self._extract_state_tuple(manager_state)
        next_outside_calls, next_inside_calls, next_current_level, next_weight, next_is_opened = self._extract_state_tuple(next_manager_state)

        outside_calls_int = self.boolean_array_to_integer(outside_calls)
        inside_calls_int = self.boolean_array_to_integer(inside_calls)
        next_outside_calls_int = self.boolean_array_to_integer(next_outside_calls)
        next_inside_calls_int = self.boolean_array_to_integer(next_inside_calls)

        # Use reward for first elevator (single elevator mode)
        r = reward[0] if isinstance(reward, list) else reward
        act = action[0].value if isinstance(action, list) else action.value

        # Q-Learning update: Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
        current_q = self.q_table[current_level, outside_calls_int, inside_calls_int, weight, is_opened, act]
        next_max_q = np.max(self.q_table[next_current_level, next_outside_calls_int, next_inside_calls_int, next_weight, next_is_opened])
        new_q = current_q + self.learning_rate * (r + self.discount_rate * next_max_q - current_q)
        self.q_table[current_level, outside_calls_int, inside_calls_int, weight, is_opened, act] = new_q

    def refresh_state(self):
        """Reset exploration rate at start of each episode"""
        self.exploration_rate = self._initial_exploration_rate

    @staticmethod
    def boolean_array_to_integer(a):
        return int(''.join(map(str, a)), 2)