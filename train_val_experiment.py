import wandb

from core.agent.utils import initialize_agent
from core.agent.train_agent import train_agent
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file, save_results
from core.agent.validate_agent import validate_agent

print(f"Training settings:"
      f" LEVELS = {Environment.LEVELS}, ELEVATORS = {Environment.ELEVATORS},"
      f" ELEVATOR WEIGHT = {Environment.ELEVATOR_WEIGHT},"
      f" EXPERIMENT NAME = {Environment.EXPERIMENT_NAME},"
      f" AGENT TYPE = {Environment.AGENT_TYPE.value},"
      f" NUMBER ELEVATORS = {Environment.ELEVATORS}, ")

wandb.init(project="ElevatorSolver", name=f"{Environment.AGENT_TYPE.value}_{Environment.EXPERIMENT_NAME}")

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
    print(f"Training completed with final reward: {train_reward[-1] if train_reward else 'N/A'}")

    # VALIDATION
    val_rewards = []
    for j in range(Environment.NUMBER_VALIDATION_PER_CASE):
        filename = f"{Environment.VALIDATE_TESTS_PATH}/validation_{j + 1}.txt"
        val_commands = read_commands_from_file(filename)
        val_reward = validate_agent(val_commands, agent)
        val_rewards.append(val_reward)
    val_average_reward = sum(val_rewards) / len(val_rewards)

    # SAVE RESULTS
    save_results(Environment.TRAIN_RESULTS_FILE_PATH, train_average_reward)
    save_results(Environment.VALIDATE_RESULTS_FILE_PATH, val_average_reward)

    wandb.log({
        "train_average_reward": train_average_reward,
        "val_average_reward": val_average_reward
    })

    print(f"Test {i + 1} processing completed!")

print("\nAll tests processed successfully!")
wandb.finish()
