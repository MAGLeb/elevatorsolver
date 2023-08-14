from utils.environment import Environment
from core.elevator import Elevator
from solution.q_table.q_table import LearningAgentQTable


NUM_EPISODES = 100
MAX_STEPS = 216000
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
    elevator = Elevator()
    state = elevator.get_state()
    total_reward = 0

    for step in range(MAX_STEPS):
        action = agent.choose_action(state)
        next_state, reward = elevator.step(action)
        agent.learn(state, action, reward, next_state)
        state = next_state
        total_reward += reward

        if np.random.rand() < 0.1:
            env.add_call(np.random.choice(env.floors)) # Randomly add calls

    print(f"Episode {episode + 1}: Total Reward: {total_reward}")

print("Training finished.")
