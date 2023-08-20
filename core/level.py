from core.passenger import Passenger
from core.types.level_type import LevelType


class Level:
    def __init__(self, level_number: int):
        self.level = level_number
        self.passengers = []
        self.type = LevelType.EMPTY

    def is_empty(self):
        return len(self.passengers) == 0

    def get_passengers_into_elevator(self):
        passengers = self.passengers.copy()
        self.passengers = []
        return passengers

    def set_outside_call(self, passenger: Passenger):
        self.passengers.append(passenger)
        self.type = LevelType.OUTSIDE_CALLED
