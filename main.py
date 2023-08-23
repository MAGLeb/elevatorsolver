from core.solution.q_table_agent.train import train as train_q_table
from utils.environment import Environment


# 1. write time, total_reward on each episode
# 2. learn: 100.000 * 100 = 10^7 * 1000 tests = 10^10

NUM_EPISODES = 100
MAX_STEPS = 86400
TEST_PATH = Environment.get_path('cases/case0/test_0.txt')
ELEVATOR_MAX_WEIGHT = 680

commands = []
with open(TEST_PATH, 'r') as f:
    line = f.readline()
    n, levels, _, _, _, _ = map(int, line.split())
    while n != 0:
        line = f.readline().strip().split()
        time, from_level, to_level, weight = line
        from_level = int(from_level)
        to_level = int(to_level)
        weight = int(weight)
        commands.append([time, from_level, to_level, weight])
        n -= 1

rewards = []

train_q_table(commands, levels, MAX_STEPS, NUM_EPISODES, ELEVATOR_MAX_WEIGHT)
