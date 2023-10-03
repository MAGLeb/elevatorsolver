import os

from dotenv import load_dotenv

from core.types.agent_type import AgentType

load_dotenv()


class Environment:
    PROJECT_PATH = os.environ.get('PROJECT_PATH')

    IS_PRODUCTION = os.environ.get('IS_PRODUCTION', 'False') == 'True'
    NUMBER_TRAIN_PER_CASE = 1000 if IS_PRODUCTION else 3
    NUMBER_VALIDATION_PER_CASE = 10 if IS_PRODUCTION else 1
    NUM_EPISODES = 100 if IS_PRODUCTION else 3
    MAX_STEPS = 86401
    ELEVATOR_MAX_WEIGHT = 680

    CASE_NUMBER = os.environ.get('CASE_NUMBER', 0)
    AGENT_TYPE = AgentType(os.environ.get('AGENT_TYPE', "Q_TABLE"))
    VALIDATION_TEST_NUMBER = 0
    UNITY_SERVER_PORT = 5000

    @classmethod
    def get_agent_path(cls):
        filepath = os.path.join(cls.PROJECT_PATH, "cases", f"case{cls.CASE_NUMBER}", f"{cls.AGENT_TYPE.value}_agent.npy")
        return filepath

    @staticmethod
    def get_path(relative_path=""):
        return os.path.join(Environment.PROJECT_PATH, relative_path)

    @staticmethod
    def get_case_path(case_number=CASE_NUMBER):
        case_path = Environment.get_path(f'cases/case{case_number}')
        return case_path

    @staticmethod
    def get_train_path(case_path):
        return f"{case_path}/train"

    @staticmethod
    def get_test_path(case_path):
        return f"{case_path}/test"

    @staticmethod
    def get_result_path(case_path):
        return f"{case_path}/result_train"

    @staticmethod
    def get_result_validate_path(case_path):
        return f"{case_path}/result_test"
