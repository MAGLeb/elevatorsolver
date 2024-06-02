import wandb
from typing import List

from core.utils.environment import Environment
from core.types.reward_type import RewardType


def initialise_settings_wandb(tags: List):
    if Environment.WANDB_KEY is not None and wandb.login(key=Environment.WANDB_KEY):
        Environment.WANDB_LOGIN = True
        print(f"Training settings:"
              f" LEVELS = {Environment.LEVELS},"
              f" ELEVATORS = {Environment.ELEVATORS},"
              f" ELEVATORS WEIGHT = {Environment.ELEVATORS_WEIGHT},"
              f" CASE NAME = {Environment.CASE_NAME},"
              f" AGENT TYPE = {Environment.AGENT_TYPE.value}.")

        if not Environment.IS_PRODUCTION:
            tags += ['local']
        else:
            tags += ['production']
        wandb.init(project="ElevatorSolver",
                   name=f"{Environment.AGENT_TYPE.value}_{Environment.CASE_NAME}",
                   tags=tags)
        wandb.config.episodes = Environment.NUM_EPISODES
        wandb.config.levels = Environment.LEVELS
        wandb.config.passability = Environment.PASSABILITY
        wandb.config.case_name = Environment.CASE_NAME
        wandb.config.elevators = Environment.ELEVATORS
        wandb.config.elevators_weight = Environment.ELEVATORS_WEIGHT
        wandb.config.agent_type = Environment.AGENT_TYPE.value
        wandb.config.reward_type = RewardType.to_string()
    else:
        print("Put WanDB key into .env: WANDB_KEY='your_key_here'")
