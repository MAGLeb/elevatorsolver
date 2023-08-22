from core.passenger import Passenger


class Level:
    def __init__(self, level_number: int):
        self.level = level_number
        self.passengers = []
        self.type = [0, 0]

    def is_empty(self):
        return len(self.passengers) == 0

    def set_outside_elevator_call(self, passenger: Passenger):
        self.passengers.append(passenger)
        self.type[0] = 1

    def set_inside_elevator_call(self):
        self.type[1] = 1
