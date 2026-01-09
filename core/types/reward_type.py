from enum import Enum


class RewardType(Enum):
    # Награды за пассажиров (пропорциональны количеству этажей)
    GET_PASSENGER = 2.0           # взял пассажира
    DELIVER_PASSENGER = 10.0      # доставил пассажира
    FAST_DELIVERY_BONUS = 2.0     # бонус за быструю доставку (умножается на коэфф)

    # Энергозатраты
    ENERGY_MOVE = -0.01           # движение (UP/DOWN)
    ENERGY_IDLE = 0               # простой

    # Штрафы за плохое поведение
    MOVE_TO_EDGE = -1.0           # попытка выехать за границу
    IDLE_WITH_CALLS = -1.0        # WAIT когда есть вызовы

    # Награды для STOP действия
    SUCCESSFUL_STOP = 0.5         # остановился где есть пассажиры
    USELESS_STOP = -1.0           # остановился но никого нет

    # Штрафы за неэффективное поведение
    MOVE_WITHOUT_PURPOSE = -1.0   # движение когда нет вызовов (было -0.3)
    MISSED_STOP = -1.0            # проехал мимо пассажира (только если не полный!)

    # Накапливающиеся штрафы (за шаг)
    WAITING_PASSENGER_PENALTY = -0.1   # за каждого ожидающего пассажира
    PASSENGER_INSIDE_PENALTY = -0.05   # за каждого пассажира внутри лифта

    @classmethod
    def to_string(cls):
        return "; ".join(f"{name.replace('_', ' ')}: {value.value}" for name, value in cls.__members__.items())
