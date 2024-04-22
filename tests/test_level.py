from core.level import Level
from core.passenger import Passenger


def test_passenger_in_out():
    from_level = 0
    to_level = 3
    passenger_weight = 70
    passengers = []
    for i in range(10):
        passengers.append(Passenger(from_level, to_level, passenger_weight))

    level = Level(4)

    passenger_in = level.get_passenger()
    assert level.outside_call == 0
    assert passenger_in is None

    level.set_outside_elevator_call(passengers[0])
    assert level.outside_call == 1
    assert len(level.passengers) == 1

    level.set_outside_elevator_call(passengers[1])
    assert level.outside_call == 1
    assert len(level.passengers) == 2

    assert level.get_passenger() == passengers[0]
    assert level.get_passenger() == passengers[0]

    assert level.pop_passenger() == passengers[0]
    assert level.outside_call == 1
    assert len(level.passengers) == 1

    assert level.pop_passenger() == passengers[1]
    assert level.outside_call == 0
    assert len(level.passengers) == 0
