import os

from core.agent.base_agent.base_agent import LearningAgentBase
from core.agent.q_table_agent.q_table_agent import LearningAgentQTable
from core.agent.dql_agent.dql_agent import LearningAgentDQL
from core.types.agent_type import AgentType
from core.manager import Manager
from core.passenger import Passenger
from core.types.reward_type import RewardType
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file
from typing import List
from core.agent.agent import Agent
from utils.utils import log


def initialize_agent(agent_type: AgentType, model_path: str = None):
    if agent_type == AgentType.Q_TABLE:
        agent = LearningAgentQTable()
    elif agent_type == AgentType.BASE:
        agent = LearningAgentBase()
    elif agent_type == AgentType.DQL:
        agent = LearningAgentDQL()
    else:
        raise ValueError(f"Type of agent: {agent_type.value} is not implemented yet.")

    if model_path is not None:
        if os.path.exists(model_path):
            agent.load(model_path)
        else:
            raise f"#### Can not find the model file! PATH: {model_path}"
    else:
        print("Start learning new model!")

    return agent


def run_episode(commands, agent, levels, elevators_weight, is_validate_run):
    manager = Manager(levels, elevators_weight)
    state = manager.get_state()
    total_reward = 0
    j = 0
    reward = [0 for _ in range(Environment.ELEVATORS)]

    for step in range(Environment.STEPS):
        manager_state = manager.manager_state
        number_passengers_wait_outside = sum(manager_state.outside_calls)
        for i in range(Environment.ELEVATORS):
            elevator_state = manager_state.elevator_states[i]
            number_passengers_wait_inside = sum(elevator_state.going_to_level)
            reward[i] -= ((number_passengers_wait_outside + number_passengers_wait_inside)
                          * RewardType.PASSENGER_WAIT.value)

        action = agent.choose_action(state)
        next_state, step_reward = manager.step(action)
        reward = [sum(x) for x in zip(step_reward, reward)]
        if not is_validate_run:
            agent.learn(state, reward, action, next_state)
        state = next_state
        total_reward += sum(reward)
        reward = [0 for _ in range(Environment.ELEVATORS)]

        while len(commands) > j:
            time, from_level, to_level, weight_passenger = commands[j]
            if step != int(time):
                break
            passenger = Passenger(from_level, to_level, weight_passenger)
            manager.add_passenger_call(passenger)
            state = manager.get_state()
            j += 1

    return total_reward


def validate_agent(agent: Agent, levels: int, elevators_weight: List):
    val_rewards = []
    for j in range(Environment.NUMBER_VALIDATION_PER_CASE):
        filename = f"{Environment.VALIDATE_TESTS_PATH}/validation_{j + 1}.txt"
        val_commands = read_commands_from_file(filename)
        val_reward = run_episode(val_commands, agent, levels, elevators_weight, True)
        val_rewards.append(val_reward)

    return val_rewards


def train_agent(commands: List[str], agent: Agent, levels: int, elevators_weight: List):
    total_rewards = []
    total_val_rewards = []

    for episode in range(Environment.NUM_EPISODES):
        reward = run_episode(commands, agent, levels, elevators_weight, False)
        total_rewards.append(reward)
        log({'train_episode_reward': reward})
        print(f"Episode {episode + 1}: \nTotal Reward: {reward}")

        # VALIDATION
        val_rewards = validate_agent(agent, Environment.LEVELS, Environment.ELEVATORS_WEIGHT)
        val_average_reward = sum(val_rewards) / len(val_rewards)
        total_val_rewards.append(val_average_reward)
        log({'val_episode_reward': val_average_reward})
        print(f"Validation reward: {val_average_reward}")

    return total_rewards, total_val_rewards
