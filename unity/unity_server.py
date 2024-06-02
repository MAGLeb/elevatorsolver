import os
from typing import List

from core.agent.utils import initialize_agent
from core.manager import Manager
from core.passenger import Passenger
from core.manager import ManagerState
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file


class UnityServer:
    def __init__(self):
        self.manager = Manager(Environment.LEVELS, Environment.ELEVATORS_WEIGHT)
        self.agent = initialize_agent(Environment.AGENT_TYPE, Environment.MODEL_FILE_PATH)
        self.agent.exploration_rate = 0

        self.commands = read_commands_from_file(
            os.path.join(Environment.VALIDATE_TESTS_PATH, 'validation_1.txt'))

        self.state = self.manager.get_state()
        self.step = 0
        self.current_command_idx = 0

    def get_next_action(self) -> (List[float], ManagerState):
        action = self.agent.choose_action(self.state)
        self.state, _ = self.manager.step(action)

        while len(self.commands) > self.current_command_idx:
            time, from_level, to_level, weight_passenger = self.commands[self.current_command_idx]
            if self.step == int(time):
                passenger = Passenger(from_level, to_level, weight_passenger)
                self.manager.add_passenger_call(passenger)
                self.state = self.manager.get_state()
                self.current_command_idx += 1
            else:
                break
        self.step += 1
        return action, self.manager.manager_state
