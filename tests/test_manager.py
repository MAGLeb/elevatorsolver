from core.manager import Manager
from core.passenger import Passenger
from core.types.action_type import ActionType


def test_manager_in_out_several_passenger():
    max_levels = 10
    elevators_weight = [680, 700]
    manager = Manager(max_levels, elevators_weight)

    state = manager.get_state()
    expected_state = [float(0) for _ in range(max_levels)]
    for i in range(len(elevators_weight)):
        elevator_state = [float(0) for _ in range(max_levels)]
        elevator_state.append(0 / max_levels)
        elevator_state.append(0 / max(elevators_weight))
        elevator_state.append(elevators_weight[i] / max(elevators_weight))
        elevator_state.append(float(0))
        expected_state += elevator_state
    assert state == expected_state

    to_level = 3
    passenger_weight = 70
    passengers = []
    for i in range(10):
        passengers.append(Passenger(i, i + to_level, passenger_weight))

    manager.add_passenger_call(passengers[0])
    manager.add_passenger_call(passengers[1])
    manager.add_passenger_call(passengers[2])

    state = manager.get_state()
    for i in range(3):
        expected_state[i] = float(1)
    assert state == expected_state

    manager.step([ActionType.UP, ActionType.OPEN_DOOR])
    state = manager.get_state()
    expected_state[0] = float(0)
    expected_state[20] = float(1 / max_levels)
    expected_state[37] = float(1)
    expected_state[27] = float(1)
    expected_state[35] = float(passenger_weight / elevators_weight[1])
    assert state == expected_state

    manager.step([ActionType.OPEN_DOOR, ActionType.CLOSE_DOOR])
    state = manager.get_state()
    expected_state[1] = float(0)
    expected_state[14] = float(1)
    expected_state[21] = float(passenger_weight / elevators_weight[0])
    expected_state[23] = float(1)
    expected_state[37] = float(0)
    assert state == expected_state

    manager.step([ActionType.CLOSE_DOOR, ActionType.UP])
    manager.step([ActionType.UP, ActionType.UP])
    manager.step([ActionType.OPEN_DOOR, ActionType.OPEN_DOOR])
    state = manager.get_state()
    expected_state[2] = float(0)
    expected_state[15] = float(1)
    expected_state[20] = float(2 / max_levels)
    expected_state[21] = float(2 * passenger_weight / elevators_weight[0])
    expected_state[23] = float(1)
    expected_state[34] = float(2 / max_levels)
    expected_state[37] = float(1)
    assert state == expected_state

    manager.step([ActionType.CLOSE_DOOR, ActionType.CLOSE_DOOR])
    manager.step([ActionType.UP, ActionType.UP])
    manager.step([ActionType.UP, ActionType.OPEN_DOOR])
    manager.step([ActionType.OPEN_DOOR, ActionType.CLOSE_DOOR])
    manager.step([ActionType.CLOSE_DOOR, ActionType.WAIT])
    manager.step([ActionType.UP, ActionType.WAIT])
    manager.step([ActionType.OPEN_DOOR, ActionType.WAIT])
    manager.step([ActionType.CLOSE_DOOR, ActionType.WAIT])
    state = manager.get_state()
    for i in range(10, 20):
        expected_state[i] = float(0)
    expected_state[20] = float(5 / max_levels)
    expected_state[21] = float(0)
    expected_state[23] = float(0)
    for i in range(24, 34):
        expected_state[i] = float(0)
    expected_state[34] = float(3 / max_levels)
    expected_state[35] = float(0)
    expected_state[37] = float(0)
    assert state == expected_state
