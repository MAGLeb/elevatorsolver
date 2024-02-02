import os

from core.agent.base_agent.base_agent import LearningAgentBase
from core.agent.q_table_agent.q_table_agent import LearningAgentQTable
from core.agent.dql_agent.dql_agent import LearningAgentDQL
from core.types.agent_type import AgentType
from core.utils.environment import Environment
from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from core.types.reward_type import RewardType


def initialize_agent():
    agent_type = Environment.AGENT_TYPE
    if agent_type == AgentType.Q_TABLE:
        agent = LearningAgentQTable()
    elif agent_type == AgentType.BASE:
        agent = LearningAgentBase()
    elif agent_type == AgentType.DQL:
        agent = LearningAgentDQL()
    else:
        raise ValueError(f"Type of agent: {agent_type.value} is not implemented yet.")

    if os.path.exists(Environment.MODEL_FILE_PATH):
        agent.load(Environment.MODEL_FILE_PATH)
    else:
        print(
            f"#### Can not find the model file! We will save model after training.\n"
            f"PATH: {Environment.MODEL_FILE_PATH}")

    return agent


def run_episode(agent, commands):
    elevator = Elevator()
    state = elevator.get_state()
    total_reward = 0
    steps_to_wait = 0
    j = 0
    reward = 0

    for step in range(Environment.STEPS):
        reward -= (sum(state[0]) + sum(state[1])) * RewardType.PASSENGER_WAIT.value

        if steps_to_wait == 0:
            action = agent.choose_action(state)
            next_state, step_reward = elevator.step(action)
            reward += step_reward
            agent.learn(state, reward, action, next_state)
            state = next_state
            total_reward += reward
            steps_to_wait = TimeWaitType.get_time_to_wait(action)
            reward = 0
        steps_to_wait = max(0, steps_to_wait - 1)

        while len(commands) > j:
            time, from_level, to_level, weight_passenger = commands[j]
            if (step % Environment.STEPS) != int(time):
                break
            passenger = Passenger(from_level, to_level, weight_passenger)
            elevator.add_call(passenger, False)
            state = elevator.get_state()
            j += 1

    return total_reward
