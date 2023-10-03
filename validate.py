import os

from core.agent.utils import initialize_agent
from core.utils.utils import read_commands_from_file, save_results
from core.agent.validate_agent import validate_agent
from core.utils.environment import Environment

case_path = Environment.get_case_path(Environment.CASE_NUMBER)
test_path = Environment.get_test_path(case_path)
os.makedirs(test_path, exist_ok=True)
results_path = Environment.get_result_validate_path(case_path)
os.makedirs(results_path, exist_ok=True)

for i in range(Environment.NUMBER_TEST_PER_CASE):
    print(f"\nProcessing test {i + 1} out of {Environment.NUMBER_TEST_PER_CASE}...")

    # READ TEST
    filename = f"{test_path}/test_{i}.txt"
    levels, commands = read_commands_from_file(filename)

    # LEARN
    agent = initialize_agent(levels, Environment.AGENT_TYPE)
    agent.exploration_rate = 0
    reward = validate_agent(commands, levels, agent)

    # SAVE RESULTS
    filename = os.path.join(results_path, f'result_{i}.txt')
    save_results(filename, reward)

    print(f"Test {i + 1} processing completed!")

print("\nAll tests processed successfully!")
