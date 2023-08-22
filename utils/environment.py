import os

import load_dotend


class Environment:
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.environ['PYTHONPATH'] = PROJECT_PATH

    IS_PRODUCTION = False
    NUMBER_TEST_PER_CASE = 1000 if IS_PRODUCTION else 3

    @staticmethod
    def get_path(relative_path=""):
        return os.path.join(Environment.PROJECT_PATH, relative_path)
