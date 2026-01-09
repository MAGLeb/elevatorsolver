import os
import wandb

from core.agent.base_agent.base_agent import LearningAgentBase
from core.agent.q_table_agent.q_table_agent import LearningAgentQTable
from core.agent.dql_agent.dql_agent import LearningAgentDQL
from core.types.action_type import ActionType
from core.types.agent_type import AgentType
from core.manager import Manager
from core.passenger import Passenger
from core.types.reward_type import RewardType
from core.utils.environment import Environment
from core.utils.utils import read_commands_from_file
from typing import List
from core.agent.agent import Agent
from core.types.case_information import CaseInformation
from core.types.stage_type import StageType

GAMMA = 0.99
INTERNAL_PASSENGER_WEIGHT = 4.0  # пассажиры внутри важнее внешних вызовов (увеличено с 2.0)


def calculate_potential(manager_state, elevator_idx):
    """
    Потенциал состояния = минус сумма расстояний до всех активных вызовов.
    Используется для potential-based reward shaping.
    Пассажиры внутри лифта имеют больший вес (приоритет на доставку).
    """
    elevator = manager_state.elevators_state[elevator_idx]
    current_level = elevator.current_level

    potential = 0
    # Расстояние до внешних вызовов (вес 1.0)
    for level, has_call in enumerate(manager_state.outside_calls):
        if has_call:
            potential -= abs(level - current_level)

    # Расстояние до целевых этажей пассажиров внутри лифта (вес 2.0 - приоритет!)
    for level, going in enumerate(elevator.going_to_level):
        if going:
            potential -= INTERNAL_PASSENGER_WEIGHT * abs(level - current_level)

    return potential


def initialize_agent(agent_type: AgentType, model_path: str = None):
    if agent_type == AgentType.Q_TABLE:
        agent = LearningAgentQTable()
    elif agent_type == AgentType.BASE:
        agent = LearningAgentBase()
    elif agent_type == AgentType.DQL:
        agent = LearningAgentDQL()
    else:
        raise ValueError(f"Type of agent: {agent_type.value} is not implemented yet.")

    if model_path is not None:
        if os.path.exists(model_path):
            agent.load(model_path)
        else:
            print(f"#### Can not find the model file! PATH: {model_path}")
    else:
        print("Start learning new model!")

    return agent


def run_episode(commands, agent, levels, elevators_weight, case_info: CaseInformation):
    manager = Manager(levels, elevators_weight)
    state = manager.get_state()
    total_reward = 0
    j = 0
    reward = [0 for _ in range(Environment.ELEVATORS)]

    for step in range(Environment.STEPS):
        case_info.step = step + case_info.episode * Environment.STEPS
        manager_state = manager.manager_state

        # Сохраняем потенциал ДО действия для potential-based shaping
        potentials_before = [calculate_potential(manager_state, i) for i in range(Environment.ELEVATORS)]

        action = agent.choose_action(state, manager_state)
        next_state, step_reward = manager.step(action, step)
        next_manager_state = manager.manager_state
        reward = [sum(x) for x in zip(step_reward, reward)]

        # Potential-based reward shaping: reward = γ·φ(s') - φ(s)
        # ВАЖНО: shaping только при обучении, не при validation!
        if case_info.stage == StageType.TRAIN:
            potentials_after = [calculate_potential(next_manager_state, i) for i in range(Environment.ELEVATORS)]
            for i in range(Environment.ELEVATORS):
                shaping_reward = GAMMA * potentials_after[i] - potentials_before[i]
                reward[i] += shaping_reward

        for i in range(Environment.ELEVATORS):
            elevator_state = manager_state.elevators_state[i]
            has_outside_calls = sum(manager_state.outside_calls) > 0
            has_inside_passengers = sum(elevator_state.going_to_level) > 0
            has_any_calls = has_outside_calls or has_inside_passengers

            # Проверка: нужно ли было остановиться на текущем этаже?
            should_stop = (
                elevator_state.going_to_level[elevator_state.current_level] > 0 or
                manager_state.outside_calls[elevator_state.current_level] > 0
            )

            # Награда/штраф за STOP
            if action[i] == ActionType.STOP:
                if should_stop:
                    reward[i] += RewardType.SUCCESSFUL_STOP.value
                else:
                    reward[i] += RewardType.USELESS_STOP.value

            # Штраф за проезд мимо пассажира (только если лифт НЕ полный!)
            is_elevator_full = elevator_state.current_weight >= elevator_state.max_weight
            if should_stop and action[i] in (ActionType.UP, ActionType.DOWN) and not is_elevator_full:
                reward[i] += RewardType.MISSED_STOP.value

            # Штраф за бездействие когда есть вызовы (WAIT)
            if action[i] == ActionType.WAIT and has_any_calls:
                reward[i] += RewardType.IDLE_WITH_CALLS.value

            # Штраф за движение без цели (UP/DOWN когда нет вызовов)
            if not has_any_calls and action[i] in (ActionType.UP, ActionType.DOWN):
                reward[i] += RewardType.MOVE_WITHOUT_PURPOSE.value

            # Накапливающиеся штрафы - создают давление забирать и доставлять быстрее
            waiting_count = sum(manager_state.outside_calls)
            inside_count = sum(elevator_state.going_to_level)
            reward[i] += waiting_count * RewardType.WAITING_PASSENGER_PENALTY.value
            reward[i] += inside_count * RewardType.PASSENGER_INSIDE_PENALTY.value

        if case_info.stage == StageType.TRAIN:
            agent.learn(state, reward, action, next_state, case_info, manager_state, next_manager_state)
        state = next_state
        total_reward += sum(reward)
        reward = [0 for _ in range(Environment.ELEVATORS)]

        while len(commands) > j:
            time, from_level, to_level, weight_passenger = commands[j]
            if step != int(time):
                break
            passenger = Passenger(from_level, to_level, weight_passenger, step)
            manager.add_passenger_call(passenger)
            state = manager.get_state()
            j += 1

    return total_reward


def validate_agent(agent: Agent, levels: int, elevators_weight: List, case_info: CaseInformation):
    val_rewards = []

    # Disable exploration during validation (pure exploitation)
    saved_exploration = getattr(agent, 'exploration_rate', None)
    if saved_exploration is not None:
        agent.exploration_rate = 0

    for j in range(Environment.NUMBER_VALIDATION_PER_CASE):
        filename = f"{Environment.VALIDATE_TESTS_PATH}/validation_{j + 1}.txt"
        val_commands = read_commands_from_file(filename)
        val_reward = run_episode(val_commands, agent, levels, elevators_weight, case_info)
        val_rewards.append(val_reward)

    # Restore exploration rate
    if saved_exploration is not None:
        agent.exploration_rate = saved_exploration

    return val_rewards


def train_val_agent(commands: List[str], agent: Agent, levels: int, elevators_weight: List, case_info: CaseInformation):
    total_rewards = []
    total_val_rewards = []

    # Early stopping and best checkpoint tracking
    best_val_reward = -float('inf')
    patience = 100
    episodes_without_improvement = 0

    for episode in range(Environment.NUM_EPISODES):
        # Reset agent state between episodes
        if hasattr(agent, 'refresh_state'):
            agent.refresh_state()

        case_info.episode = (episode + 1) * case_info.case
        case_info.stage = StageType.TRAIN
        learning_reward = run_episode(commands, agent, levels, elevators_weight, case_info)
        total_rewards.append(learning_reward)
        print(f"Episode {episode + 1}: \nTotal Reward: {learning_reward}")

        # VALIDATION
        case_info.stage = StageType.VALIDATE
        val_rewards = validate_agent(agent, Environment.LEVELS, Environment.ELEVATORS_WEIGHT, case_info)
        val_average_reward = sum(val_rewards) / len(val_rewards)
        total_val_rewards.append(val_average_reward)
        print(f"Validation reward: {val_average_reward}")

        # Best checkpoint saving
        if val_average_reward > best_val_reward:
            best_val_reward = val_average_reward
            episodes_without_improvement = 0
            agent.save(Environment.MODEL_FILE_PATH)
            print(f"New best validation: {best_val_reward:.2f} - checkpoint saved!")
        else:
            episodes_without_improvement += 1

        wandb.log({
            'case_test_number': case_info.case,
            'episode': case_info.episode,
            'train_episode_reward': learning_reward,
            'val_episode_reward': val_average_reward,
            'best_val_reward': best_val_reward,
        })

        # Early stopping
        if episodes_without_improvement >= patience:
            print(f"Early stopping: no improvement for {patience} episodes")
            break

    return total_rewards, total_val_rewards
