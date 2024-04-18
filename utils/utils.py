import wandb

from core.utils.environment import Environment


def initialise_settings_wandb():
    if Environment.WANDB_KEY is not None and wandb.login(key="457fdbdea5069b232a4d4ef6a50dfb036f734a70"):
        Environment.WANDB_LOGIN = True
        print(f"Training settings:"
              f" LEVELS = {Environment.LEVELS},"
              f" ELEVATORS = {Environment.ELEVATORS},"
              f" ELEVATORS WEIGHT = {Environment.ELEVATORS_WEIGHT},"
              f" CASE NAME = {Environment.CASE_NAME},"
              f" AGENT TYPE = {Environment.AGENT_TYPE.value}.")

        wandb.init(project="ElevatorSolver", name=f"{Environment.AGENT_TYPE.value}_{Environment.CASE_NAME}")
        wandb.config.episodes = Environment.NUM_EPISODES
        wandb.config.levels = Environment.LEVELS
        wandb.config.passability = Environment.PASSABILITY
        wandb.config.case_name = Environment.CASE_NAME
        wandb.config.elevators = Environment.ELEVATORS
        wandb.config.elevators_weight = Environment.ELEVATORS_WEIGHT
        wandb.config.agent_type = Environment.AGENT_TYPE.value
    else:
        print("Put WanDB key into .env: WANDB_KEY='your_key_here'")


def log(message):
    if Environment.WANDB_LOGIN:
        wandb.log(message)
    else:
        print(message)
