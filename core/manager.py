from typing import List

from core.level import Level
from core.elevator import Elevator
from core.utils.elevator_info import ElevatorInfo
from core.types.action_type import ActionType
from core.types.state_elevator import StateElevator


class Manager:
    def __init__(self, max_levels: int, elevators_info: List[ElevatorInfo]):
        self.max_level = max_levels
        self.elevators = [Elevator(max_levels, elevators_info[i].max_weight) for i in range(len(elevators_info))]
        self.levels = [Level(i) for i in range(self.max_level)]
        self.max_elevators_weight = max(elevators_info[i].max_weight for i in range(len(elevators_info)))

    def step(self, actions: List[ActionType]) -> int:
        reward = 0
        for i, elevator in enumerate(self.elevators):
            action = actions[i]
            reward += elevator.step(action, self.levels)

        return reward

    def get_state(self) -> List[float]:
        state = [float(level.outside_call) for level in self.levels]
        for i, elevator in enumerate(self.elevators):
            state_elevator = elevator.get_state()
            state += self._convert_state_elevator_into_list(state_elevator)

        return state

    def _convert_state_elevator_into_list(self, state: StateElevator) -> List[float]:
        # Map from wide space to [0, 1] range output. It is help NN learn better.
        scaled_state = []
        scaled_state += list(map(float, state.going_to_level))
        scaled_state.append(state.current_level / self.max_level)
        scaled_state.append(state.current_weight / self.max_elevators_weight)
        scaled_state.append(state.max_weight / self.max_elevators_weight)
        scaled_state.append(float(state.is_open_door))

        return scaled_state
