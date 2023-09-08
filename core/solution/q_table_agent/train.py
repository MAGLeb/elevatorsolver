import os

from core.utils.environment import Environment
from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType
from core.solution.q_table_agent.utils import calculate_exploration_fall
from core.solution.q_table_agent.q_table_agent import LearningAgentQTable


def train(commands, levels, agent_path):
    max_steps = Environment.MAX_STEPS
    num_episodes = Environment.NUM_EPISODES
    max_weight = Environment.ELEVATOR_MAX_WEIGHT
    exploration_fall = calculate_exploration_fall(max_steps)

    agent = LearningAgentQTable(levels, exploration_fall=exploration_fall)
    if os.path.exists(f'{agent_path}.npy'):
        agent.load(f'{agent_path}.npy')
    total_rewards = []

    for episode in range(num_episodes):
        commands_copy = commands.copy()
        agent.reset_exploration_rate()
        elevator = Elevator(levels, max_weight)
        state = elevator.get_state()
        total_reward = 0
        steps_to_wait = 0

        for step in range(max_steps):
            if steps_to_wait == 0:
                action = agent.choose_action(state)
                next_state, reward = elevator.step(action)
                agent.learn(state, reward, action, next_state)
                state = next_state
                total_reward += reward
                steps_to_wait = TimeWaitType.get_time_to_wait(action)
            steps_to_wait = max(0, steps_to_wait - 1)

            while len(commands_copy) > 0:
                time, from_level, to_level, weight_passenger = commands_copy[0]
                if (step % max_steps) != int(time):
                    break
                passenger = Passenger(from_level, to_level, weight_passenger)
                elevator.add_call(from_level, False, passenger)
                state = elevator.get_state()
                commands_copy.pop(0)

        total_rewards.append(total_reward)
        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    agent.save(agent_path)
    print(f"max:{max(total_rewards)}, average:{sum(total_rewards) / num_episodes}")
    print("Training finished.")
    return total_rewards
