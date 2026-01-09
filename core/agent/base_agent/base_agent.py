from typing import List, Optional
from enum import Enum

from core.agent.agent import Agent
from core.types.action_type import ActionType
from core.utils.environment import Environment


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

    def choose_action(self, state: List[float], manager_state=None) -> List[ActionType]:
        if manager_state is None:
            return [ActionType.WAIT for _ in range(Environment.ELEVATORS)]

        actions = []
        for i, elevator_state in enumerate(manager_state.elevators_state):
            current_level = elevator_state.current_level

            # Проверяем есть ли вообще вызовы
            has_outside_calls = sum(manager_state.outside_calls) > 0
            has_inside_passengers = sum(elevator_state.going_to_level) > 0
            has_any_calls = has_outside_calls or has_inside_passengers

            # Если нет вызовов - ждём
            if not has_any_calls:
                action = ActionType.WAIT
            else:
                # Проверяем нужно ли остановиться на текущем этаже
                should_stop = (
                    elevator_state.going_to_level[current_level] > 0 or
                    manager_state.outside_calls[current_level] > 0
                )

                if should_stop:
                    action = ActionType.STOP
                elif self.direction == Direction.UP:
                    action = ActionType.UP
                    if current_level + 2 >= len(manager_state.outside_calls):
                        self.direction = Direction.DOWN
                elif self.direction == Direction.DOWN:
                    action = ActionType.DOWN
                    if current_level <= 1:
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

    def learn(self, state, reward, action, next_state, case_info, manager_state=None, next_manager_state=None):
        pass
