from core.utils.environment import Environment
from core.elevator import Elevator
from core.passenger import Passenger
from core.types.time_wait_type import TimeWaitType


def train_agent(commands, agent):
    total_rewards = []

    for episode in range(Environment.NUM_EPISODES):
        commands_copy = commands.copy()
        elevator = Elevator()
        state = elevator.get_state()
        total_reward = 0
        steps_to_wait = 0

        for step in range(Environment.STEPS):
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
                if (step % Environment.STEPS) != int(time):
                    break
                passenger = Passenger(from_level, to_level, weight_passenger)
                elevator.add_call(from_level, False, passenger)
                state = elevator.get_state()
                commands_copy.pop(0)

        total_rewards.append(total_reward)
        print(f"Episode {episode + 1}: Total Reward: {total_reward}")

    return total_rewards
