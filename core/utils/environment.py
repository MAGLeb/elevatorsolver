import os
import yaml
import random
import string
import shutil

from dotenv import load_dotenv

from core.types.agent_type import AgentType

load_dotenv()


class Environment:
    PROJECT_PATH = os.environ.get('PROJECT_PATH')
    IS_PRODUCTION = os.environ.get('IS_PRODUCTION', 'False') == 'True'

    # CASE params
    NUMBER_TRAIN_PER_CASE = None
    NUMBER_VALIDATION_PER_CASE = None
    LEVELS = None
    PASSABILITY = None
    ELEVATORS = None

    # EXPERIMENT params
    EXPERIMENT_NAME = None
    NUM_EPISODES = None
    AGENT_TYPE = None
    ELEVATOR_WEIGHT = None
    # Each step is a second on the daytime. We set 90000 more than seconds
    # on the day, to give extra time for Elevator to process all the passengers.
    STEPS = 90000

    # PATHS
    VALIDATE_TESTS_PATH = None
    TRAIN_TESTS_PATH = None
    MODEL_FILE_PATH = None
    VALIDATE_RESULTS_FILE_PATH = None
    TRAIN_RESULTS_FILE_PATH = None

    UNITY_SERVER_PORT = 5000

    def __init__(self):
        self._initialisation_environment()
        self._initialize_folders()

    @classmethod
    def _initialisation_environment(cls):
        config_path = os.path.join(cls.PROJECT_PATH, "config.yml")
        with open(config_path, "r") as file:
            params = yaml.safe_load(file)
            experiment_params = params['experiment_params']

        # Initialisation params from experiment_params
        cls.LEVELS = experiment_params.get('levels', 10)
        cls.PASSABILITY = experiment_params.get('passability', 7200)
        cls.ELEVATORS = experiment_params.get('elevators', 1)
        cls.NUMBER_TRAIN_PER_CASE = experiment_params.get('train_tests', 1000 if cls.IS_PRODUCTION else 3)
        cls.NUMBER_VALIDATION_PER_CASE = experiment_params.get('validation_tests', 10 if cls.IS_PRODUCTION else 1)
        cls.AGENT_TYPE = AgentType(experiment_params.get('agent_type', "DQL"))
        cls.NUM_EPISODES = experiment_params.get('episodes', 100 if cls.IS_PRODUCTION else 3)
        cls.ELEVATOR_WEIGHT = 680
        # cls.ELEVATOR_WEIGHT = experiment_params.get('elevator_weight', 680)

        cls.EXPERIMENT_NAME = experiment_params.get('experiment_name')
        if cls.EXPERIMENT_NAME is None:
            cls.EXPERIMENT_NAME = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))

    @classmethod
    def _update_experiment_name_in_copied_config(cls, copied_config_path):
        with open(copied_config_path, 'r') as file:
            config_data = yaml.safe_load(file)

        config_data['experiment_params']['experiment_name'] = cls.EXPERIMENT_NAME

        with open(copied_config_path, 'w') as file:
            yaml.safe_dump(config_data, file)

    @classmethod
    def _initialize_folders(cls):
        cases_path = os.path.join(cls.PROJECT_PATH, "cases")
        os.makedirs(cases_path, exist_ok=True)

        case_path = os.path.join(cases_path, f"case_{cls.LEVELS}_{cls.ELEVATORS}")
        os.makedirs(case_path, exist_ok=True)

        tests_path = os.path.join(case_path, "tests")
        os.makedirs(tests_path, exist_ok=True)

        cls.VALIDATE_TESTS_PATH = os.path.join(tests_path, "validation")
        os.makedirs(cls.VALIDATE_TESTS_PATH, exist_ok=True)

        cls.TRAIN_TESTS_PATH = os.path.join(tests_path, "train")
        os.makedirs(cls.TRAIN_TESTS_PATH, exist_ok=True)

        experiments_path = os.path.join(case_path, "experiments")
        os.makedirs(experiments_path, exist_ok=True)

        experiment_path = os.path.join(experiments_path, f"{cls.AGENT_TYPE.value}_{cls.EXPERIMENT_NAME}")
        os.makedirs(experiment_path, exist_ok=True)

        shutil.copy(os.path.join(cls.PROJECT_PATH, "config.yml"), experiment_path)
        cls._update_experiment_name_in_copied_config(os.path.join(experiment_path, "config.yml"))

        results_path = os.path.join(experiment_path, "results")
        os.makedirs(results_path, exist_ok=True)

        cls.MODEL_FILE_PATH = os.path.join(experiment_path, "model.npy")
        cls.VALIDATE_RESULTS_FILE_PATH = os.path.join(results_path, "validation.txt")
        cls.TRAIN_RESULTS_FILE_PATH = os.path.join(results_path, "train.txt")
