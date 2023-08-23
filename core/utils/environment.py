import os

from dotenv import load_dotenv

load_dotenv()


class Environment:
    PROJECT_PATH = os.environ.get('PYTHONPATH')
    IS_PRODUCTION = os.environ.get('IS_PRODUCTION', 'False') == 'True'

    @staticmethod
    def get_path(relative_path=""):
        return os.path.join(Environment.PROJECT_PATH, relative_path)
