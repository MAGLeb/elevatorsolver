from abc import ABC, abstractmethod
import math

from core.types.action_type import ActionType
from core.utils.environment import Environment


class Agent(ABC):
    @abstractmethod
    def __init__(self):
        self.levels = Environment.LEVELS
        self.exploration_fall = self.calculate_exploration_fall()

    @abstractmethod
    def choose_action(self, state) -> ActionType:
        pass

    @abstractmethod
    def save(self, *args, **params):
        pass

    @abstractmethod
    def learn(self, *args, **params):
        pass

    @abstractmethod
    def reset_exploration_rate(self, *args, **params):
        pass

    @staticmethod
    def calculate_exploration_fall():
        """
        First fifth part of all commands, we do exploration then move to take best action from table.
        """
        steps = Environment.STEPS
        t = math.log10(0.5)
        y = int(steps / 5)
        return 10 ** (t / y)
