from core.solution.agent import Agent
from core.types.action_type import ActionType


class LearningAgentBase(Agent):
    def __init__(self, levels):
        super().__init__(levels)

    @staticmethod
    def _find_level_to_go(outside_call_levels, inside_call_levels):
        if len(inside_call_levels) > 0:
            return min(inside_call_levels)
        return min(outside_call_levels)

    def choose_action(self, state) -> ActionType:
        outside_calls, inside_calls, current_level, weight, is_opened = state

        if is_opened:
            return ActionType.CLOSE_DOOR
        is_outside_call = len([i for i in outside_calls if i == 1]) != 0
        is_inside_call = len([i for i in inside_calls if i == 1]) != 0
        if not is_outside_call and not is_inside_call:
            return ActionType.WAIT
        outside_call_levels = [i for i in range(len(outside_calls)) if outside_calls[i] == 1]
        inside_call_levels = [i for i in range(len(inside_calls)) if inside_calls[i] == 1]

        if current_level in outside_call_levels or current_level in inside_call_levels:
            return ActionType.OPEN_DOOR

        level_to_go = self._find_level_to_go(outside_call_levels, inside_call_levels)

        if current_level < level_to_go:
            return ActionType.UP
        else:
            return ActionType.DOWN
