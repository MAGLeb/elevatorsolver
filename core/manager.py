from typing import List

from core.level import Level
from core.elevator import Elevator
from core.types.action_type import ActionType
from core.elevator import StateElevator
from core.passenger import Passenger


class ManagerState:
    def __init__(self, outside_calls: List[int], elevator_states: List[StateElevator], max_level: int, max_elevators_weight: int):
        self.outside_calls = outside_calls
        self.elevator_states = elevator_states
        self.max_level = max_level
        self.max_elevators_weight = max_elevators_weight

    def __str__(self):
        outside_calls_str = f"  Outside calls: {self.outside_calls}\n"

        elevator_states_str = ""
        for elevator_state in self.elevator_states:
            elevator_states_str += f"    Elevator: {elevator_state}\n"

        # Combine the formatted strings into a single representation
        return f"Manager State:\n{outside_calls_str}{elevator_states_str}"


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

        return self.manager_state(), reward

    def manager_state(self) -> ManagerState:
        outside_calls = [level.outside_call for level in self.levels]
        elevator_states = []
        for i, elevator in enumerate(self.elevators):
            state_elevator = elevator.get_state()
            elevator_states.append(state_elevator)

        manager_state = ManagerState(outside_calls, elevator_states, self.max_level, self.max_elevators_weight)
        return manager_state
