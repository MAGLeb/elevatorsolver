from typing import List

from core.types.action_type import ActionType
from core.types.reward_type import RewardType
from core.level import Level


class StateElevator:
    def __init__(self, going_to_level: List[int], current_level: int, current_weight: int, max_weight: int, is_open_door: int):
        self.going_to_level = going_to_level
        self.current_level = current_level
        self.current_weight = current_weight
        self.max_weight = max_weight
        self.is_open_door = is_open_door

    def __eq__(self, other):
        if not isinstance(other, StateElevator):
            return NotImplemented
        return (self.going_to_level == other.going_to_level and
                self.current_level == other.current_level and
                self.current_weight == other.current_weight and
                self.max_weight == other.max_weight and
                self.is_open_door == other.is_open_door)

    def __str__(self):
        return (f"Elevator State:\n"
                f"  Current Level: {self.current_level}\n"
                f"  Going to Levels: {self.going_to_level}\n"
                f"  Current Weight: {self.current_weight} kg\n"
                f"  Maximum Weight: {self.max_weight} kg\n"
                f"  Door Open: {'Yes' if self.is_open_door else 'No'}")


class Elevator:
    def __init__(self, max_levels: int, max_weight: int):
        self.max_levels = max_levels
        self.max_weight = max_weight

        self.passengers = []
        self.going_to_level = [0 for _ in range(max_levels)]
        self.current_weight = 0
        self.current_level = 0
        self.is_door_open = False

    def step(self, action: ActionType, levels: List[Level], current_step: int = 0) -> int:
        # Двери открываются ТОЛЬКО при действии STOP
        if action == ActionType.STOP:
            should_open = (
                self.going_to_level[self.current_level] > 0 or
                levels[self.current_level].outside_call > 0
            )
            if should_open:
                return self._handle_door(levels, current_step)
            # STOP но некого обслуживать - просто стоим
            return RewardType.ENERGY_IDLE.value

        # UP/DOWN/WAIT - НЕ открывают двери
        if action == ActionType.UP:
            return self._up()
        elif action == ActionType.DOWN:
            return self._down()
        else:  # WAIT
            return RewardType.ENERGY_IDLE.value

    def _get_passengers_into_elevator(self, levels: List[Level]) -> int:
        passengers = 0
        level = levels[self.current_level]

        while level.get_passenger() is not None:
            if self.max_weight < self.current_weight + level.get_passenger().weight:
                break
            passenger = level.pop_passenger()
            self.current_weight += passenger.weight
            self.going_to_level[passenger.to_level] = 1
            passengers += 1
            self.passengers.append(passenger)

        return passengers * RewardType.GET_PASSENGER.value

    def _get_out_passengers_from_elevator(self, current_step: int = 0) -> int:
        reward = 0
        max_fast_steps = self.max_levels  # быстрая доставка = меньше шагов чем этажей

        for p in self.passengers:
            if p.to_level == self.current_level:
                self.current_weight -= p.weight
                wait_time = current_step - getattr(p, 'spawn_step', 0)
                base_reward = RewardType.DELIVER_PASSENGER.value

                # Бонус за быструю доставку (если доставил быстрее чем кол-во этажей)
                if wait_time <= max_fast_steps:
                    bonus = RewardType.FAST_DELIVERY_BONUS.value * (1 - wait_time / max_fast_steps)
                else:
                    bonus = 0

                reward += base_reward + bonus
        self.passengers = [p for p in self.passengers if p.to_level != self.current_level]

        return reward

    def get_state(self) -> StateElevator:
        state = StateElevator(self.going_to_level, self.current_level,
                              self.current_weight, self.max_weight, self.is_door_open)
        return state

    def _up(self):
        reward = RewardType.ENERGY_MOVE.value
        if self.current_level == self.max_levels - 1:
            reward += RewardType.MOVE_TO_EDGE.value
        else:
            self.current_level += 1
        return reward

    def _down(self):
        reward = RewardType.ENERGY_MOVE.value
        if self.current_level == 0:
            reward += RewardType.MOVE_TO_EDGE.value
        else:
            self.current_level -= 1
        return reward

    def _handle_door(self, levels: List[Level], current_step: int = 0):
        self.is_door_open = True
        reward = 0
        reward += self._get_out_passengers_from_elevator(current_step)
        self.going_to_level[self.current_level] = 0
        reward += self._get_passengers_into_elevator(levels)
        self.is_door_open = False
        return reward
