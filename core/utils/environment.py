import os

from dotenv import load_dotenv

load_dotenv()


class Environment:
    PROJECT_PATH = os.environ.get('PROJECT_PATH')
    IS_PRODUCTION = os.environ.get('IS_PRODUCTION', 'False') == 'True'
    NUMBER_TEST_PER_CASE = 1000 if IS_PRODUCTION else 3

    @staticmethod
    def get_path(relative_path=""):
        return os.path.join(Environment.PROJECT_PATH, relative_path)

    @staticmethod
    def get_case_path(case_number):
        case_path = Environment.get_path(f'cases/case{case_number}')
        return case_path
