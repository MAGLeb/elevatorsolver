import os

from core.solution.utils import initialize_agent
from core.solution.train_agent import train_agent
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file, save_results

print(f"Training settings: NUM_EPISODES = {Environment.NUM_EPISODES},"
      f" MAX_STEPS = {Environment.MAX_STEPS}, ELEVATOR_MAX_WEIGHT = {Environment.ELEVATOR_MAX_WEIGHT}")
print(f"Total tests to be processed: {Environment.NUMBER_TRAIN_PER_CASE}")

case_path = Environment.get_case_path(Environment.CASE_NUMBER)
train_path = Environment.get_train_path(case_path)
os.makedirs(train_path, exist_ok=True)
results_path = Environment.get_result_path(case_path)
os.makedirs(results_path, exist_ok=True)

for i in range(Environment.NUMBER_TRAIN_PER_CASE):
    print(f"\nProcessing test {i + 1} out of {Environment.NUMBER_TRAIN_PER_CASE}...")

    # READ TEST
    filename = f"{train_path}/train_{i}.txt"
    levels, commands = read_commands_from_file(filename)

    # LEARN
    print(f"Starting training Q-Table agent...")
    agent = initialize_agent(levels, Environment.AGENT_TYPE)
    reward = train_agent(commands, levels, agent)
    print(f"Training completed with final reward: {reward[-1] if reward else 'N/A'}")

    # SAVE RESULTS
    filename = os.path.join(results_path, f'result_{i}.txt')
    save_results(filename, reward)

    print(f"Test {i + 1} processing completed!")

print("\nAll tests processed successfully!")
