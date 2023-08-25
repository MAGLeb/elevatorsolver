import os

from core.solution.q_table_agent.train import train as train_q_table
from core.utils.environment import Environment

NUM_EPISODES = 100
MAX_STEPS = 86400
ELEVATOR_MAX_WEIGHT = 680

print(f"Training settings: NUM_EPISODES = {NUM_EPISODES},"
      f" MAX_STEPS = {MAX_STEPS}, ELEVATOR_MAX_WEIGHT = {ELEVATOR_MAX_WEIGHT}")
print(f"Total tests to be processed: {Environment.NUMBER_TEST_PER_CASE}")

for i in range(Environment.NUMBER_TEST_PER_CASE):
    print(f"\nProcessing test {i + 1} out of {Environment.NUMBER_TEST_PER_CASE}...")

    # READ TEST
    commands = []
    case_path = Environment.get_case_path(1)
    test_path = os.path.join(case_path, f'tests/test{i}.txt')
    print(f"Reading test data from {test_path}")
    with open(test_path, 'r') as f:
        line = f.readline()
        n, levels, _, _, _, _ = line.split()
        n = int(n)
        levels = int(levels)
        while n != 0:
            line = f.readline().strip().split()
            time, from_level, to_level, weight = line
            from_level = int(from_level)
            to_level = int(to_level)
            weight = int(weight)
            commands.append([time, from_level, to_level, weight])
            n -= 1

    print(f"Read {len(commands)} commands from test data.")

    # LEARN
    agent_path = os.path.join(case_path, 'q_table_agent')
    print(f"Starting training Q-Table agent...")
    reward = train_q_table(commands, levels, MAX_STEPS, NUM_EPISODES, ELEVATOR_MAX_WEIGHT, agent_path)
    print(f"Training completed with final reward: {reward[-1] if reward else 'N/A'}")

    # SAVE RESULTS
    results_path = os.path.join(case_path, f'results')
    os.makedirs(results_path, exist_ok=True)
    result_path = os.path.join(results_path, f'result{i}.txt')
    print(f"Saving results to {result_path}")
    with open(result_path, 'w') as f:
        f.writelines(map(lambda x: str(x) + '\n', reward))
    print(f"Test {i + 1} processing completed!")

print("\nAll tests processed successfully!")
