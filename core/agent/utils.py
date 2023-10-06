import os

from core.agent.base_agent.base_agent import LearningAgentBase
from core.agent.q_table_agent.q_table_agent import LearningAgentQTable
from core.agent.dql_agent.dql_agent import LearningAgentDQL
from core.types.agent_type import AgentType
from core.utils.environment import Environment


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
