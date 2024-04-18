from core.passenger import Passenger


class Level:
    def __init__(self, level_number: int):
        self.level = level_number
        self.passengers = []
        self.outside_call = 0

    def set_outside_elevator_call(self, passenger: Passenger):
        self.passengers.append(passenger)
        self.outside_call = 1

    def get_passenger(self):
        if len(self.passengers) == 0:
            return None
        return self.passengers[0]

    def pop_passenger(self):
        passenger = self.passengers.pop(0)
        return passenger
