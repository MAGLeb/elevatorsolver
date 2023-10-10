import os

from core.agent.utils import initialize_agent
from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from core.types.action_type import ActionType
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file


class UnityServer:
    def __init__(self):
        self.commands = read_commands_from_file(
            os.path.join(Environment.VALIDATE_TESTS_PATH, 'validation_4.txt'))
        self.agent = initialize_agent()
        self.agent.exploration_rate = 0
        self.elevator = Elevator()
        self.state = self.elevator.get_state()
        self.steps_to_wait = 0
        self.step = 0
        self.number_command = 0

    def get_next_action(self):
        action = ActionType.WAIT
        if self.steps_to_wait == 0:
            action = self.agent.choose_action(self.state)
            next_state, _ = self.elevator.step(action)
            self.state = next_state
            self.steps_to_wait = TimeWaitType.get_time_to_wait(action)
        self.steps_to_wait = max(0, self.steps_to_wait - 1)

        while len(self.commands) > self.number_command:
            time, from_level, to_level, weight_passenger = self.commands[self.number_command]
            if (self.step % Environment.STEPS) == int(time):
                passenger = Passenger(from_level, to_level, weight_passenger)
                self.elevator.add_call(passenger, False)
                self.state = self.elevator.get_state()
                self.number_command += 1
            else:
                break
        self.step += 1
        return action.value, self.state[0], self.state[1]
