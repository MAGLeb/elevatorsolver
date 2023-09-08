import os
from abc import ABC, abstractmethod

from core.types.action_type import ActionType
from core.types.agent_type import AgentType
from core.utils.environment import Environment


class Agent(ABC):
    @abstractmethod
    def __init__(self, levels):
        self.levels = levels

    @abstractmethod
    def choose_action(self, state) -> ActionType:
        pass
