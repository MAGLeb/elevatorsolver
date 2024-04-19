from core.elevator import Elevator, StateElevator
from core.level import Level
from core.passenger import Passenger
from core.types.action_type import ActionType
from core.types.reward_type import RewardType


def test_move_out_of_edges_with_open_door():
    max_levels = 3
    max_weight = 500
    elevator = Elevator(max_levels, max_weight)
    levels = [Level(i) for i in range(max_levels)]
    going_to = [0 for _ in range(max_levels)]

    elevator.step(ActionType.OPEN_DOOR, levels)
    reward = elevator.step(ActionType.UP, levels)
    reward_expected = RewardType.MOVE_WITH_OPEN_DOOR.value + RewardType.UP_DOWN_STEP.value
    assert reward_expected == reward

    elevator.step(ActionType.UP, levels)
    reward = elevator.step(ActionType.UP, levels)
    reward_expected = RewardType.MOVE_NEXT_TO_EDGE.value + RewardType.UP_DOWN_STEP.value + RewardType.MOVE_WITH_OPEN_DOOR.value
    assert reward_expected == reward

    elevator.step(ActionType.UP, levels)
    elevator.step(ActionType.UP, levels)
    elevator.step(ActionType.UP, levels)
    elevator_state_target = StateElevator(going_to, 2, 0, max_weight, 1)
    assert are_elevator_states_equal(elevator, elevator_state_target)

    elevator.step(ActionType.CLOSE_DOOR, levels)
    elevator.step(ActionType.DOWN, levels)
    elevator.step(ActionType.DOWN, levels)
    elevator.step(ActionType.DOWN, levels)
    elevator.step(ActionType.DOWN, levels)
    elevator.step(ActionType.DOWN, levels)
    elevator_state_target = StateElevator(going_to, 0, 0, max_weight, 0)
    assert are_elevator_states_equal(elevator, elevator_state_target)


def test_several_passenger():
    """
    Test several passengers in and out.
    Test max passengers in Elevator.
    """

    max_levels = 5
    max_weight = 220
    elevator = Elevator(max_levels, max_weight)
    levels = [Level(i) for i in range(max_levels)]
    going_to = [0 for _ in range(max_levels)]

    from_level = 0
    to_level = 3
    passenger_weight = 70
    for i in range(10):
        passenger = Passenger(from_level, to_level, passenger_weight)
        levels[passenger.from_level].set_outside_elevator_call(passenger)

    reward = elevator.step(ActionType.OPEN_DOOR, levels)
    going_to[to_level] = 1
    reward_expected = RewardType.GET_PASSENGER.value * 3 + RewardType.OPEN_CLOSE_DOOR.value
    assert reward_expected == reward
    elevator_state_target = StateElevator(going_to, 0, passenger_weight * 3, max_weight, 1)
    assert are_elevator_states_equal(elevator, elevator_state_target)

    elevator.step(ActionType.CLOSE_DOOR, levels)
    elevator.step(ActionType.UP, levels)
    elevator.step(ActionType.UP, levels)
    elevator.step(ActionType.UP, levels)
    reward = elevator.step(ActionType.OPEN_DOOR, levels)
    going_to[to_level] = 0
    reward_expected = RewardType.DELIVER_PASSENGER.value * 3 + RewardType.OPEN_CLOSE_DOOR.value
    assert reward_expected == reward
    elevator_state_target = StateElevator(going_to, 3, 0, max_weight, 1)
    assert are_elevator_states_equal(elevator, elevator_state_target)


def test_get_out_passenger():
    """
    Test passenger go from 0 level to 3 level.
    """

    max_levels = 5
    max_weight = 500
    elevator = Elevator(max_levels, max_weight)
    levels = [Level(i) for i in range(max_levels)]
    going_to = [0 for _ in range(max_levels)]

    passenger = Passenger(0, 3, 72)
    levels[passenger.from_level].set_outside_elevator_call(passenger)

    elevator_state_target = StateElevator(going_to, 0, 0, max_weight, 0)
    assert are_elevator_states_equal(elevator, elevator_state_target)

    reward = elevator.step(ActionType.OPEN_DOOR, levels)
    going_to[passenger.to_level] = 1
    reward_expected = RewardType.GET_PASSENGER.value + RewardType.OPEN_CLOSE_DOOR.value
    assert reward_expected == reward

    elevator_state_target = StateElevator(going_to, 0, 72, max_weight, 1)
    assert are_elevator_states_equal(elevator, elevator_state_target)

    reward = elevator.step(ActionType.CLOSE_DOOR, levels)
    reward_expected = RewardType.OPEN_CLOSE_DOOR.value
    assert reward_expected == reward

    for i in range(3):
        reward = elevator.step(ActionType.UP, levels)
        reward_expected = RewardType.UP_DOWN_STEP.value
        assert reward_expected == reward

    elevator_state_target = StateElevator(going_to, 3, 72, max_weight, 0)
    assert are_elevator_states_equal(elevator, elevator_state_target)

    reward = elevator.step(ActionType.OPEN_DOOR, levels)
    going_to[passenger.to_level] = 0
    reward_expected = RewardType.OPEN_CLOSE_DOOR.value + RewardType.DELIVER_PASSENGER.value * 1
    assert reward_expected == reward
    elevator_state_target = StateElevator(going_to, 3, 0, max_weight, 1)
    assert are_elevator_states_equal(elevator, elevator_state_target)


def are_elevator_states_equal(elevator, elevator_state_target):
    elevator_state_real = elevator.get_state()
    return elevator_state_target == elevator_state_real
