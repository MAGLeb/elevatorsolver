from core.solution.agent import Agent
from core.types.action_type import ActionType


class LearningAgentBase(Agent):
    def __init__(self, levels):
        super().__init__(levels)

        self.level_to_go = None

    @staticmethod
    def _find_level_to_go(outside_call_levels, inside_call_levels):
        if len(inside_call_levels) > 0:
            return min(inside_call_levels)
        return max(outside_call_levels)

    def _go_down_or_up(self, current_level):
        if current_level < self.level_to_go:
            return ActionType.UP
        else:
            return ActionType.DOWN

    def choose_action(self, state) -> ActionType:
        outside_calls, inside_calls, current_level, weight, is_opened = state

        if self.level_to_go is not None and current_level < self.level_to_go:
            return self._go_down_or_up(current_level)

        if is_opened:
            return ActionType.CLOSE_DOOR
        is_outside_call = len([i for i in outside_calls if i == 1]) != 0
        is_inside_call = len([i for i in inside_calls if i == 1]) != 0
        if not is_outside_call and not is_inside_call:
            return ActionType.WAIT
        outside_call_levels = [i for i in range(len(outside_calls)) if outside_calls[i] == 1]
        inside_call_levels = [i for i in range(len(inside_calls)) if inside_calls[i] == 1]

        if (current_level in outside_call_levels and weight < 7) or (current_level in inside_call_levels):
            return ActionType.OPEN_DOOR

        self.level_to_go = self._find_level_to_go(outside_call_levels, inside_call_levels)
        return self._go_down_or_up(current_level)

    def save(self):
        pass

    def learn(self):
        pass

    def reset_exploration_rate(self):
        pass
