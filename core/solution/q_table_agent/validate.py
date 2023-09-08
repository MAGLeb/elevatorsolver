import os

from core.utils.environment import Environment
from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from core.solution.q_table_agent.q_table_agent import LearningAgentQTable


def validate(commands, levels, agent_path):
    max_steps = Environment.MAX_STEPS
    max_weight = Environment.ELEVATOR_MAX_WEIGHT

    agent = LearningAgentQTable(levels, exploration_rate=0)
    if os.path.exists(f'{agent_path}.npy'):
        agent.load(f'{agent_path}.npy')
    else:
        raise ValueError("Can not find the model file.")

    elevator = Elevator(levels, max_weight)
    state = elevator.get_state()
    total_reward = 0
    steps_to_wait = 0

    for step in range(max_steps):
        if steps_to_wait == 0:
            action = agent.choose_action(state)
            next_state, reward = elevator.step(action)
            state = next_state
            total_reward += reward
            steps_to_wait = TimeWaitType.get_time_to_wait(action)
        steps_to_wait = max(0, steps_to_wait - 1)

        while len(commands) > 0:
            time, from_level, to_level, weight_passenger = commands[0]
            if (step % max_steps) != int(time):
                break
            passenger = Passenger(from_level, to_level, weight_passenger)
            elevator.add_call(from_level, False, passenger)
            state = elevator.get_state()
            commands.pop(0)

    print(f"Total Reward: {total_reward}")
    print("Testing finished.")

    return [total_reward]
