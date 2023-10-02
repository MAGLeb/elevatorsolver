from abc import ABC, abstractmethod

from core.types.action_type import ActionType


class Agent(ABC):
    @abstractmethod
    def __init__(self, levels):
        self.levels = levels

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
