from core.agent.utils import initialize_agent
from core.agent.utils import train_agent
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file, save_results
from case_generation.generate import generate_tests

from utils.utils import initialise_settings_wandb, log


# TEST GENERATION
generate_tests(Environment.VALIDATE_TESTS_PATH, "validation", Environment.NUMBER_VALIDATION_PER_CASE)
generate_tests(Environment.TRAIN_TESTS_PATH, "train", Environment.NUMBER_TRAIN_PER_CASE)
print("All train and test cases generated successfully!")

# SETTINGS WANDB
initialise_settings_wandb()

# TRAIN & VALIDATE & SAVE
max_val_reward = -float('inf')
for i in range(Environment.NUMBER_TRAIN_PER_CASE):
    print(f"\nProcessing test {i + 1} out of {Environment.NUMBER_TRAIN_PER_CASE}...")

    # READ TEST
    filename = f"{Environment.TRAIN_TESTS_PATH}/train_{i + 1}.txt"
    commands = read_commands_from_file(filename)

    # LEARN & VALIDATION
    print(f"Starting training {Environment.AGENT_TYPE.value} agent...")
    agent = initialize_agent(Environment.AGENT_TYPE)
    train_reward, validation_reward = train_agent(commands, agent, Environment.LEVELS, Environment.ELEVATORS_WEIGHT)

    train_average_reward = sum(train_reward) / Environment.NUM_EPISODES
    print(f"Training completed with average reward: {train_average_reward}")
    valid_average_reward = sum(validation_reward) / Environment.NUM_EPISODES
    print(f"Validation completed with average reward: {valid_average_reward}")

    # SAVE RESULTS
    save_results(Environment.TRAIN_RESULTS_FILE_PATH, train_average_reward)
    save_results(Environment.VALIDATE_RESULTS_FILE_PATH, valid_average_reward)

    if valid_average_reward > max_val_reward:
        max_val_reward = valid_average_reward
        agent.save(Environment.MODEL_FILE_PATH)

    log({
        "train_average_reward": train_average_reward,
        "val_average_reward": valid_average_reward
    })

    print(f"Test {i + 1} processing completed!")

print("\nAll tests processed successfully!")
