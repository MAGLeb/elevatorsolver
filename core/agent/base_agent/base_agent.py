from typing import List

from core.agent.agent import Agent
from core.types.action_type import ActionType
from core.utils.environment import Environment
from core.elevator import StateElevator
from core.manager import ManagerState


class QueuePastActions:
    def __init__(self, queue_size: int = 5):
        self.size = queue_size
        self.actions = [ActionType.WAIT for _ in range(self.size)]

    def add(self, action: ActionType):
        self.actions.append(action)
        if len(self.actions) > self.size:
            self.actions = self.actions[:-self.size]

    def get(self, prev_action_order):
        if prev_action_order >= self.size:
            raise ValueError(f"Queue store only {self.size} past actions.")
        action_order = self.size - prev_action_order
        return self.actions[action_order]


class LearningAgentBase(Agent):
    def __init__(self):
        Agent.__init__(self)

        self.prev_actions = [QueuePastActions() for _ in range(Environment.ELEVATORS)]

    def choose_action(self, state: List[float]) -> List[ActionType]:
        outside_calls, elevators_state = parse_state(state)
        actions = []
        for i, elevator_state in enumerate(elevators_state):
            if elevator_state.is_open_door:
                actions.append(ActionType.CLOSE_DOOR)
            elif outside_calls[elevator_state.current_level] == float(1) and self.prev_actions[
                i] != ActionType.CLOSE_DOOR:
                actions.append(ActionType.OPEN_DOOR)
            elif any(elevator_state.going_to_level) == float(1):
                level_to_go = find_level_to_go(elevator_state.going_to_level, elevator_state.current_level)
                action = go_down_or_up(elevator_state.current_level, level_to_go)
                actions.append(action)
            else:
                actions.append(ActionType.WAIT)
        return actions

    def save(self, filepath):
        pass

    def learn(self, state, reward, action, next_state):
        pass


def parse_state(state: List[float]) -> (List[int], List[StateElevator]):
    outside_calls = state[:Environment.LEVELS]
    elevators_state = []

    for i in range(Environment.ELEVATORS):
        going_to, current_level, current_weight, max_weight, is_open_door = state[
                                                                            StateElevator.__len__() * (i + 1):]
        elevator_state = StateElevator(going_to, current_level, current_weight, max_weight, is_open_door)
        elevators_state.append(elevator_state)

    return outside_calls, elevators_state


def go_down_or_up(current_level, level_to_go):
    if current_level < level_to_go:
        return ActionType.UP
    else:
        return ActionType.DOWN


def find_level_to_go(going_to: List[float], current_level: int):
    nearest_level = [float("inf"), None]
    for i, level in enumerate(going_to):
        if level == float(1):
            diff = abs(current_level - level)
            if diff < nearest_level[0]:
                nearest_level = [diff, i]
    return nearest_level[1]
