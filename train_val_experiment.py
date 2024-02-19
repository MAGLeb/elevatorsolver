import wandb

from core.agent.utils import initialize_agent
from core.agent.train_agent import train_agent
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file, save_results
from core.agent.utils import run_episode
from case_generation.generate import generate_tests


# TEST GENERATION
generate_tests(Environment.VALIDATE_TESTS_PATH, "validation", Environment.NUMBER_VALIDATION_PER_CASE)
generate_tests(Environment.TRAIN_TESTS_PATH, "train", Environment.NUMBER_TRAIN_PER_CASE)
print("All train and test cases generated successfully!")

# SETTINGS WANDB
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

# TRAIN & VALIDATE & SAVE
for i in range(Environment.NUMBER_TRAIN_PER_CASE):
    print(f"\nProcessing test {i + 1} out of {Environment.NUMBER_TRAIN_PER_CASE}...")

    # READ TEST
    filename = f"{Environment.TRAIN_TESTS_PATH}/train_{i + 1}.txt"
    commands = read_commands_from_file(filename)

    # LEARN
    print(f"Starting training {Environment.AGENT_TYPE.value} agent...")
    agent = initialize_agent()
    train_reward = train_agent(commands, agent)
    train_average_reward = sum(train_reward) / Environment.NUM_EPISODES
    print(f"Training completed with average reward: {train_average_reward}")

    # VALIDATION
    max_val_reward = -float('inf')
    val_rewards = []
    for j in range(Environment.NUMBER_VALIDATION_PER_CASE):
        filename = f"{Environment.VALIDATE_TESTS_PATH}/validation_{j + 1}.txt"
        val_commands = read_commands_from_file(filename)
        val_reward = run_episode(agent, val_commands)
        val_rewards.append(val_reward)
    val_average_reward = sum(val_rewards) / len(val_rewards)
    print(f"Validating completed with average reward: {val_average_reward}")

    # SAVE RESULTS
    save_results(Environment.TRAIN_RESULTS_FILE_PATH, train_average_reward)
    save_results(Environment.VALIDATE_RESULTS_FILE_PATH, val_average_reward)

    if val_average_reward > max_val_reward:
        max_val_reward = val_average_reward
        agent.save(Environment.MODEL_FILE_PATH)

    wandb.log({
        "train_average_reward": train_average_reward,
        "val_average_reward": val_average_reward
    })

    print(f"Test {i + 1} processing completed!")

print("\nAll tests processed successfully!")
wandb.finish()
