from core.utils.environment import Environment
from core.agent.utils import run_episode


def train_agent(commands, agent):
    total_rewards = []

    for episode in range(Environment.NUM_EPISODES):
        commands_copy = commands.copy()
        reward = run_episode(agent, commands_copy)

        total_rewards.append(reward)
        print(f"Episode {episode + 1}: Total Reward: {reward}")

    return total_rewards
