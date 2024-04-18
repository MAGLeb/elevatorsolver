import os
import yaml
import random
import string
import shutil
import hashlib

from dotenv import load_dotenv

from core.types.agent_type import AgentType

load_dotenv()


class Environment:
    PROJECT_PATH = os.environ.get('PROJECT_PATH')
    IS_PRODUCTION = os.environ.get('IS_PRODUCTION', 'False') == 'True'
    WANDB_KEY = os.environ.get('WANDB_KEY', None)
    WANDB_LOGIN = False

    # CASE params
    NUMBER_TRAIN_PER_CASE = None
    NUMBER_VALIDATION_PER_CASE = None
    LEVELS = None
    PASSABILITY = None
    ELEVATORS = None
    DAYS = None

    # EXPERIMENT params
    CASE_NAME = None
    NUM_EPISODES = None
    AGENT_TYPE = None
    ELEVATORS_WEIGHT = None

    # PATHS
    VALIDATE_TESTS_PATH = None
    TRAIN_TESTS_PATH = None
    MODEL_FILE_PATH = None
    VALIDATE_RESULTS_FILE_PATH = None
    TRAIN_RESULTS_FILE_PATH = None

    UNITY_SERVER_PORT = 5000

    # Each step is a second on the daytime. We set 90000 more than seconds
    # on the day, to give extra time for Elevator to process all the passengers.
    STEPS = None

    def __init__(self):
        self._initialisation_environment()
        self._initialize_folders()

    @classmethod
    def _initialisation_environment(cls):
        config_path = os.path.join(cls.PROJECT_PATH, "config.yml")
        with open(config_path, "r") as file:
            params = yaml.safe_load(file)
            data_params = params['data_params']
            case_params = params['case_params']

        # Initialisation params from Case
        cls.LEVELS = data_params.get('levels', 10)
        cls.PASSABILITY = data_params.get('passability', 7200)
        cls.NUMBER_TRAIN_PER_CASE = data_params.get('train_tests', 1000 if cls.IS_PRODUCTION else 3)
        cls.NUMBER_VALIDATION_PER_CASE = data_params.get('validation_tests', 10 if cls.IS_PRODUCTION else 1)
        cls.DAYS = data_params.get('days', 7 if cls.IS_PRODUCTION else 1)
        cls.STEPS = 87000 * cls.DAYS

        # Initialisation params from Experiment
        cls.ELEVATORS = case_params.get('elevators', 1)
        cls.AGENT_TYPE = AgentType(case_params.get('agent_type', "DQL"))
        cls.NUM_EPISODES = case_params.get('episodes', 20 if cls.IS_PRODUCTION else 3)
        cls.ELEVATORS_WEIGHT = case_params.get('elevator_weight', [680 for _ in range(cls.ELEVATORS)])
        cls.CASE_NAME = case_params.get('case_name')
        if cls.CASE_NAME is None:
            cls.CASE_NAME = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7))

    @classmethod
    def _create_case_config(cls, path):
        shutil.copy(os.path.join(cls.PROJECT_PATH, "config.yml"), path)
        config_path = os.path.join(path, "config.yml")
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)

        config_data['case_params']['case_name'] = cls.CASE_NAME

        with open(config_path, 'w') as file:
            yaml.safe_dump(config_data, file)

    @classmethod
    def _create_data_config(cls, path):
        config_path = os.path.join(path, "config.yml")
        if not os.path.exists(config_path):
            shutil.copy(os.path.join(cls.PROJECT_PATH, "config.yml"), path)
            config_path = os.path.join(path, "config.yml")
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)

            del config_data['case_params']

            with open(config_path, 'w') as file:
                yaml.safe_dump(config_data, file)

    @classmethod
    def _initialize_folders(cls):
        experiments_path = os.path.join(cls.PROJECT_PATH, "experiments")
        data_path = os.path.join(experiments_path, "data")
        os.makedirs(data_path, exist_ok=True)

        data_folder_name = hashlib.sha256(
            f"{cls.LEVELS} {cls.DAYS} {cls.PASSABILITY}"
            f" {cls.NUMBER_TRAIN_PER_CASE} {cls.NUMBER_VALIDATION_PER_CASE}".encode()).hexdigest()[:8]
        data_path = os.path.join(data_path, data_folder_name)
        os.makedirs(data_path, exist_ok=True)
        cls._create_data_config(data_path)

        cls.VALIDATE_TESTS_PATH = os.path.join(data_path, "validation")
        os.makedirs(cls.VALIDATE_TESTS_PATH, exist_ok=True)

        cls.TRAIN_TESTS_PATH = os.path.join(data_path, "train")
        os.makedirs(cls.TRAIN_TESTS_PATH, exist_ok=True)

        cases_path = os.path.join(experiments_path, "cases")
        os.makedirs(cases_path, exist_ok=True)

        cases_path = os.path.join(cases_path, f"{cls.AGENT_TYPE.value}_{cls.CASE_NAME}")
        os.makedirs(cases_path, exist_ok=True)
        cls._create_case_config(cases_path)

        results_path = os.path.join(cases_path, "results")
        os.makedirs(results_path, exist_ok=True)

        cls.MODEL_FILE_PATH = os.path.join(cases_path, "model.npy")
        cls.VALIDATE_RESULTS_FILE_PATH = os.path.join(results_path, "validation.txt")
        cls.TRAIN_RESULTS_FILE_PATH = os.path.join(results_path, "train.txt")


Environment()
