import os

from core.solution.q_table_agent.train import train as train_q_table
from core.utils.environment import Environment

# learn: 100.000 * 100 = 10^7 * 1000 tests = 10^10

NUM_EPISODES = 100
MAX_STEPS = 86400
ELEVATOR_MAX_WEIGHT = 680

for i in range(Environment.NUMBER_TEST_PER_CASE):
    # READ TEST
    commands = []
    case_path = Environment.get_case_path(0)
    test_path = os.path.join(case_path, f'tests/test{i}.txt')
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

    # LEARN
    agent_path = os.path.join(case_path, 'q_table_agent')
    reward = train_q_table(commands, levels, MAX_STEPS, NUM_EPISODES, ELEVATOR_MAX_WEIGHT, agent_path)
    # SAVE RESULTS
    results_path = os.path.join(case_path, f'results')
    os.makedirs(results_path, exist_ok=True)
    result_path = os.path.join(results_path, f'result{i}.txt')
    with open(result_path, 'w') as f:
        f.writelines(map(lambda x: str(x) + '\n', reward))
