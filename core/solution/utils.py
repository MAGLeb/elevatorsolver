import os
import math

from core.solution.base_agent.base_agent import LearningAgentBase
from core.solution.q_table_agent.q_table_agent import LearningAgentQTable
from core.solution.dql_agent.dql_agent import LearningAgentDQL
from core.types.agent_type import AgentType
from core.utils.environment import Environment


def initialize_agent(levels: int, agent_type: AgentType):
    if agent_type == AgentType.Q_TABLE:
        agent = LearningAgentQTable(levels)
    elif agent_type == AgentType.BASE:
        agent = LearningAgentBase(levels)
    elif agent_type == AgentType.DQN:
        agent = LearningAgentDQL(levels)
    else:
        raise ValueError(f"Type of agent: {agent_type.value} is not implemented yet.")

    if os.path.exists(Environment.get_agent_path()):
        agent.load(Environment.get_agent_path())
    else:
        print(
            f"#### Can not find the model file! We will initialize empty model. \nPATH: {Environment.get_agent_path()}")

    return agent


def calculate_exploration_fall(number_commands):
    """
    First fifth part of all commands, we do exploration then move to take best action from table.
    """
    t = math.log10(0.5)
    y = int(number_commands / 5)
    return 10 ** (t / y)


def boolean_array_to_integer(a):
    return int(''.join(map(str, a)), 2)
