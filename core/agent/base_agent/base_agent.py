from typing import List
from enum import Enum

from core.agent.agent import Agent
from core.types.action_type import ActionType
from core.utils.environment import Environment
from core.manager import ManagerState


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"


class QueuePastActions:
    def __init__(self, queue_size: int = 5):
        self.size = queue_size
        self.actions = [ActionType.WAIT for _ in range(self.size)]

    def add(self, action: ActionType):
        self.actions.append(action)
        if len(self.actions) > self.size:
            self.actions = self.actions[-self.size:]

    def get(self, prev_action_order: int = 1):
        if prev_action_order >= self.size:
            raise ValueError(f"Queue store only {self.size} past actions.")
        action_order = self.size - prev_action_order
        return self.actions[action_order]


class LearningAgentBase(Agent):
    def __init__(self):
        Agent.__init__(self)

        self.prev_actions = [QueuePastActions() for _ in range(Environment.ELEVATORS)]
        self.direction = Direction.UP

    def choose_action(self, manager_state: ManagerState) -> List[ActionType]:
        actions = []
        for i, elevator_state in enumerate(manager_state.elevator_states):
            if elevator_state.is_open_door:
                action = ActionType.CLOSE_DOOR
            elif (((manager_state.outside_calls[elevator_state.current_level] == 1 and
                  self.prev_actions[i].get() != ActionType.CLOSE_DOOR) and
                  elevator_state.current_weight / elevator_state.max_weight < 0.7) or
                  (elevator_state.going_to_level[elevator_state.current_level] == 1)):
                action = ActionType.OPEN_DOOR
            elif self.direction == Direction.UP:
                action = ActionType.UP
                if elevator_state.current_level + 2 == manager_state.max_level:
                    self.direction = Direction.DOWN
            elif self.direction == Direction.DOWN:
                action = ActionType.DOWN
                if elevator_state.current_level - 1 == 0:
                    self.direction = Direction.UP
            else:
                action = ActionType.WAIT

            self.prev_actions[i].add(action)
            actions.append(action)
        return actions

    def refresh_state(self):
        self.prev_actions = [QueuePastActions() for _ in range(Environment.ELEVATORS)]
        self.direction = Direction.UP

    def save(self, filepath):
        pass

    def learn(self, state, reward, action, next_state, case_info):
        pass
