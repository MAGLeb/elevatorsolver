from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from solution.q_table_agent.q_table_agent import LearningAgentQTable
from utils.environment import Environment

NUM_EPISODES = 100
MAX_STEPS = 86400
TEST_PATH = Environment.get_path('cases/case0/test_0.txt')


def train():
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

    agent = LearningAgentQTable(levels)
    agent.load('1.npy')
    total_rewards = []

    for episode in range(NUM_EPISODES):
        elevator_max_weight = 680
        elevator = Elevator(levels, elevator_max_weight)
        state = elevator.get_state()
        total_reward = 0
        steps_to_wait = 0

        for step in range(MAX_STEPS * 10):
            if steps_to_wait == 0:
                action = agent.choose_action(state)
                next_state, reward = elevator.step(action)
                agent.learn(state, reward, action, next_state)
                state = next_state
                total_reward += reward
                steps_to_wait = TimeWaitType.get_time_to_wait(action)
            steps_to_wait = max(0, steps_to_wait - 1)

            if len(commands) > 0:
                time, from_level, to_level, weight_passenger = commands[0]
                if (step % MAX_STEPS) == int(time):
                    passenger = Passenger(from_level, to_level, weight_passenger)
                    elevator.add_call(from_level, False, passenger)
                    state = elevator.get_state()
                    commands.pop(0)

        total_rewards.append(total_reward)
        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    agent.save('1')
    print(f"max:{max(total_rewards)}, average:{sum(total_rewards) / NUM_EPISODES}")
    print("Training finished.")
