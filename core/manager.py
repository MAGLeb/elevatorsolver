from typing import List

from core.level import Level
from core.elevator import Elevator
from core.types.action_type import ActionType
from core.elevator import StateElevator
from core.passenger import Passenger


class ManagerState:
    def __init__(self, outside_calls: List[float], elevator_states: List[StateElevator]):
        self.outside_calls = outside_calls
        self.elevator_states = elevator_states


class Manager:
    def __init__(self, max_levels: int, elevators_weight: List):
        self.max_level = max_levels
        self.elevators = [Elevator(max_levels, elevators_weight[i]) for i in range(len(elevators_weight))]
        self.levels = [Level(i) for i in range(self.max_level)]
        self.max_elevators_weight = max(elevators_weight[i] for i in range(len(elevators_weight)))

    def add_passenger_call(self, passenger: Passenger):
        passenger_level = passenger.from_level
        self.levels[passenger_level].set_outside_elevator_call(passenger)

    def step(self, actions: List[ActionType]) -> [List[float], int]:
        reward = []
        for i, elevator in enumerate(self.elevators):
            action = actions[i]
            reward.append(elevator.step(action, self.levels))

        return self.get_state(), reward

    @property
    def manager_state(self) -> ManagerState:
        outside_calls = [float(level.outside_call) for level in self.levels]
        elevator_states = []
        for i, elevator in enumerate(self.elevators):
            state_elevator = elevator.get_state()
            elevator_states.append(state_elevator)

        manager_state = ManagerState(outside_calls, elevator_states)
        return manager_state

    def get_state(self) -> List[float]:
        manager_state = self.manager_state
        state = manager_state.outside_calls

        for elevator_state in manager_state.elevator_states:
            state += self._convert_state_elevator_into_list(elevator_state)

        return state

    def _convert_state_elevator_into_list(self, state: StateElevator) -> List[float]:
        # Map from wide space to [0, 1] range output. It is help NN learn better.
        scaled_state = []
        scaled_state += list(map(float, state.going_to_level))
        scaled_state.append(state.current_level / self.max_level)
        scaled_state.append(state.current_weight / state.max_weight)
        scaled_state.append(state.max_weight / self.max_elevators_weight)
        scaled_state.append(float(state.is_open_door))

        return scaled_state
