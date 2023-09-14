from core.solution.utils import initialize_agent
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file
from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from core.types.action_type import ActionType

TEST_NUMBER = Environment.VALIDATION_TEST_NUMBER
CASE_PATH = Environment.get_case_path(Environment.CASE_NUMBER)
TEST_PATH = Environment.get_test_path(CASE_PATH)
FILENAME = f"{TEST_PATH}/test_{TEST_NUMBER}.txt"


class UnityServer:
    def __init__(self):
        self.levels, self.commands = read_commands_from_file(FILENAME)
        self.agent = initialize_agent(self.levels, Environment.AGENT_TYPE)
        self.agent.exploration_rate = 0
        self.max_steps = Environment.MAX_STEPS
        self.elevator = Elevator(self.levels, Environment.ELEVATOR_MAX_WEIGHT)
        self.state = self.elevator.get_state()
        self.steps_to_wait = 0
        self.step = 0

    def get_next_action(self):
        action = ActionType.EMPTY
        if self.steps_to_wait == 0:
            action = self.agent.choose_action(self.state)
            next_state, _ = self.elevator.step(action)
            self.state = next_state
            self.steps_to_wait = TimeWaitType.get_time_to_wait(action)
        self.steps_to_wait = max(0, self.steps_to_wait - 1)

        while len(self.commands) > 0:
            time, from_level, to_level, weight_passenger = self.commands[0]
            if (self.step % self.max_steps) == int(time):
                passenger = Passenger(from_level, to_level, weight_passenger)
                self.elevator.add_call(from_level, False, passenger)
                self.state = self.elevator.get_state()
                self.commands.pop(0)
            else:
                break
        self.step += 1
        return action.value, self.state[0], self.state[1]
