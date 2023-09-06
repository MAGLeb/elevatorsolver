import os

from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from core.solution.q_table_agent.q_table_agent import LearningAgentQTable


def train(commands, levels, max_steps, num_episodes, max_weight, agent_path):
    agent = LearningAgentQTable(levels)
    if os.path.exists(f'{agent_path}.npy'):
        agent.load(f'{agent_path}.npy')
    total_rewards = []

    for episode in range(num_episodes):
        elevator_max_weight = max_weight
        elevator = Elevator(levels, elevator_max_weight)
        state = elevator.get_state()
        total_reward = 0
        steps_to_wait = 0

        for step in range(max_steps * 3):
            if steps_to_wait == 0:
                action = agent.choose_action(state)
                next_state, reward = elevator.step(action)
                agent.learn(state, reward, action, next_state)
                state = next_state
                total_reward += reward
                steps_to_wait = TimeWaitType.get_time_to_wait(action)
            steps_to_wait = max(0, steps_to_wait - 1)

            if len(commands) > 0:
                while len(commands) > 0:
                    time, from_level, to_level, weight_passenger = commands[0]
                    if (step % max_steps) != int(time):
                        break
                    passenger = Passenger(from_level, to_level, weight_passenger)
                    elevator.add_call(from_level, False, passenger)
                    state = elevator.get_state()
                    commands.pop(0)

        total_rewards.append(total_reward)
        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    agent.save(agent_path)
    print(f"max:{max(total_rewards)}, average:{sum(total_rewards) / num_episodes}")
    print("Training finished.")
    return total_rewards
