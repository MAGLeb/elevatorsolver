import wandb

from core.agent.utils import initialize_agent
from core.agent.utils import train_val_agent
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file, save_results
from case_generation.generate import generate_tests
from core.utils.logger import GlobalLogger
from core.types.case_information import CaseInformation

from utils.utils import initialise_settings_wandb

# SETTINGS WANDB
initialise_settings_wandb()

with GlobalLogger() as logger:
    try:
        # TEST GENERATION
        generate_tests(Environment.VALIDATE_TESTS_PATH, "validation", Environment.NUMBER_VALIDATION_PER_CASE)
        generate_tests(Environment.TRAIN_TESTS_PATH, "train", Environment.NUMBER_TRAIN_PER_CASE)
        print("All train and test cases generated successfully!")

        # TRAIN & VALIDATE & SAVE
        max_val_reward = -float('inf')
        for i in range(Environment.NUMBER_TRAIN_PER_CASE):
            case_info = CaseInformation(i)
            print(f"\nProcessing test {i + 1} out of {Environment.NUMBER_TRAIN_PER_CASE}...")

            # READ TEST
            filename = f"{Environment.TRAIN_TESTS_PATH}/train_{i + 1}.txt"
            commands = read_commands_from_file(filename)

            # LEARN & VALIDATION
            print(f"Starting training {Environment.AGENT_TYPE.value} agent...")
            agent = initialize_agent(Environment.AGENT_TYPE, Environment.MODEL_FILE_PATH)
            train_reward, validation_reward = train_val_agent(commands, agent,
                                                          Environment.LEVELS,
                                                          Environment.ELEVATORS_WEIGHT,
                                                          case_info)

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

            wandb.log({
                "case_test_number": i,
                "train_average_reward": train_average_reward,
                "val_average_reward": valid_average_reward
            })

            print(f"Test {i + 1} processing completed!")

        print("\nAll tests processed successfully!")

    except Exception as e:
        raise e
