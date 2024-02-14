from typing import List


class StateElevator:
    def __init__(self, going_to_level: List[int], current_level: int, current_weight: int, max_weight: int, is_open_door: int):
        self.going_to_level = going_to_level
        self.current_level = current_level
        self.current_weight = current_weight
        self.max_weight = max_weight
        self.is_open_door = is_open_door
