from utils.environment import Environment
from core.elevator import Elevator
from solution.q_table.q_table import LearningAgentQTable
from core.level_type import LevelType
from core.time_wait_type import TimeWaitType


NUM_EPISODES = 100
MAX_STEPS = 86400
TEST_PATH = Environment.get_path('./cases/case_1/test_0')

commands = []
with open(TEST_PATH, 'r') as f:
    line = f.readline()
    n, levels, _, _, _, _ = map(int, line.split())
    while n != 0:
        line = f.readline().strip().split()
        time, from_level, to_level = line
        from_level = int(from_level)
        to_level = int(to_level)
        commands.append([time, from_level, to_level])
        n -= 1


agent = LearningAgentQTable(levels)

for episode in range(NUM_EPISODES):
    elevator = Elevator(levels)
    state = elevator.get_state()
    total_reward = 0
    steps_to_wait = 0

    for step in range(MAX_STEPS):
        if steps_to_wait == 0:
            action = agent.choose_action(state)
            next_state, reward = elevator.step(action)
            agent.learn(state, action, reward, next_state)
            state = next_state
            total_reward += reward
            steps_to_wait = TimeWaitType.get_time_to_wait(action)
            steps_to_wait = max(0, steps_to_wait - 1)

        time, from_level, to_level = commands[len(commands) - 1][0]
        if step == time:
            elevator.add_call(from_level, LevelType.GET_PASSENGER)
            elevator.add_call(to_level, LevelType.OUT_PASSENGER)
            commands.pop(len(commands) - 1)

    print(f"Episode {episode + 1}: Total Reward: {total_reward}")

print("Training finished.")
