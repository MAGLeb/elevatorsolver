import os

from core.solution.base_agent.base_agent import LearningAgentBase
from core.solution.q_table_agent.q_table_agent import LearningAgentQTable
from core.types.agent_type import AgentType
from core.utils.environment import Environment


def initialize_agent(levels: int, agent_type: AgentType):
    if agent_type == AgentType.Q_TABLE:
        agent = LearningAgentQTable(levels)
        if os.path.exists(Environment.get_agent_path()):
            agent.load(Environment.get_agent_path())
        else:
            print(f"#### Can not find the model file!!! \nPATH: {Environment.get_agent_path()}")
    elif agent_type == AgentType.BASE:
        agent = LearningAgentBase(levels)
    else:
        raise ValueError(f"Type of agent: {agent_type.value} is not implemented yet.")

    return agent
