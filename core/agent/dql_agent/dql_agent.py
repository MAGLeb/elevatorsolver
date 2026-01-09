import copy
import random
from collections import namedtuple, deque
from typing import List

import wandb
import torch
import torch.nn as nn
import torch.optim as optim

from core.agent.agent import Agent
from core.types.action_type import ActionType
from core.utils.environment import Environment


Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'next_action_mask'))


class ReplayBuffer:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class LearningAgentDQL(nn.Module, Agent):
    def __init__(self, learning_rate=0.0001, exploration_rate=1.0, buffer_size=4500, batch_size=64):
        nn.Module.__init__(self)
        Agent.__init__(self)

        self.learning_rate = learning_rate
        self.buffer_size = buffer_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.buffer = ReplayBuffer(buffer_size)
        self.batch_size = batch_size

        # outside_levels, inside_levels for each elevator
        # current_level, current_weight, door_state, max_weight for each elevator
        self.fc1 = nn.Linear(self.levels + self.levels * self.elevators + 4 * self.elevators, 1024)
        self.fc2 = nn.Linear(1024, 512)
        self.rnn = nn.LSTM(512, 256, num_layers=2, batch_first=True)
        self.fc3 = nn.Linear(256, len(ActionType) * self.elevators)

        self.dropout = nn.Dropout(p=0.5)
        self.relu = nn.LeakyReLU()
        self.loss_function = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        self.gamma = 0.99
        self.exploration_rate = exploration_rate
        self._initial_exploration_rate = exploration_rate
        self.exploration_fall = 0.99991  # 1.0 → 0.01 за ~50000 шагов (~10 эпизодов)
        self.min_exploration = 0.01  # Минимум 1% exploration

        # Target Network для стабильности обучения
        self.target_update_freq = 500  # Обновлять каждые 500 шагов
        self.learn_step_counter = 0

        self.to(self.device)

        # Создаём target network как копию основной сети
        self.target_net = self._create_target_network()

        self.log_model_params()

    def _create_target_network(self):
        """Создаёт копию сети для target network"""
        target = nn.Sequential(
            nn.Linear(self.levels + self.levels * self.elevators + 4 * self.elevators, 1024),
            nn.LeakyReLU(),
            nn.Linear(1024, 512),
            nn.LeakyReLU(),
        ).to(self.device)

        # Копируем веса для первых слоёв
        target[0].weight.data = self.fc1.weight.data.clone()
        target[0].bias.data = self.fc1.bias.data.clone()
        target[2].weight.data = self.fc2.weight.data.clone()
        target[2].bias.data = self.fc2.bias.data.clone()

        # Для LSTM и fc3 создаём отдельные копии
        self.target_rnn = nn.LSTM(512, 256, num_layers=2, batch_first=True).to(self.device)
        self.target_rnn.load_state_dict(self.rnn.state_dict())

        self.target_fc3 = nn.Linear(256, len(ActionType) * self.elevators).to(self.device)
        self.target_fc3.weight.data = self.fc3.weight.data.clone()
        self.target_fc3.bias.data = self.fc3.bias.data.clone()

        return target

    def _update_target_network(self):
        """Копирует веса из основной сети в target network"""
        self.target_net[0].weight.data = self.fc1.weight.data.clone()
        self.target_net[0].bias.data = self.fc1.bias.data.clone()
        self.target_net[2].weight.data = self.fc2.weight.data.clone()
        self.target_net[2].bias.data = self.fc2.bias.data.clone()
        self.target_rnn.load_state_dict(self.rnn.state_dict())
        self.target_fc3.weight.data = self.fc3.weight.data.clone()
        self.target_fc3.bias.data = self.fc3.bias.data.clone()

    def _forward_target(self, x):
        """Forward pass через target network"""
        x = self.target_net(x)
        x = x.unsqueeze(1)
        x, _ = self.target_rnn(x)
        x = x[:, -1, :]
        x = self.target_fc3(x)
        return x

    def log_model_params(self):
        # TODO rewrite.
        # Method should return architecture of model without writing to WanDB.
        architecture_str = []

        for layer in self.children():
            if isinstance(layer, nn.Linear):
                layer_str = f"Linear({layer.in_features}, {layer.out_features})"
            elif isinstance(layer, nn.Conv2d):
                layer_str = f"Conv2d({layer.in_channels}, {layer.out_channels}, kernel_size={layer.kernel_size})"
            elif isinstance(layer, nn.Dropout):
                layer_str = f"Dropout(p={layer.p})"
            elif isinstance(layer, nn.ReLU):
                layer_str = "ReLU"
            elif isinstance(layer, nn.BatchNorm2d):
                layer_str = f"BatchNorm2d({layer.num_features})"
            else:
                layer_str = f"UnknownLayer({type(layer).__name__})"

            architecture_str.append(layer_str)

        architecture = " -> ".join(architecture_str)
        if wandb.run is not None:
            wandb.config.architecture = architecture
            wandb.config.learning_rate = self.learning_rate
            wandb.config.buffer_size = self.buffer_size
            wandb.config.batch_size = self.batch_size

    def load(self, filepath):
        checkpoint = torch.load(filepath)
        self.load_state_dict(checkpoint['model_state_dict'], strict=False)
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        # Синхронизируем target network с загруженными весами
        self._update_target_network()

    def save(self, filepath):
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filepath)

    def choose_action(self, state, manager_state=None) -> List[ActionType]:
        if manager_state is None:
            return [ActionType.WAIT for _ in range(self.elevators)]

        actions = []
        self.exploration_rate = max(
            self.min_exploration,
            self.exploration_rate * self.exploration_fall
        )

        state_tensor = self._convert_elevator_state_to_tensor(state)
        output = self.forward(state_tensor)

        for i in range(self.elevators):
            elevator_state = manager_state.elevators_state[i]
            current_level = elevator_state.current_level
            max_level = len(manager_state.outside_calls) - 1

            # Создаём маску допустимых действий [UP, DOWN, WAIT, STOP]
            action_mask = [True, True, True, True]

            # Границы этажей
            if current_level >= max_level:
                action_mask[0] = False  # запретить UP
            if current_level <= 0:
                action_mask[1] = False  # запретить DOWN

            # Пассажир на этаже → только STOP/WAIT
            should_stop = (
                elevator_state.going_to_level[current_level] > 0 or
                manager_state.outside_calls[current_level] > 0
            )
            if should_stop:
                action_mask[0] = False  # запретить UP
                action_mask[1] = False  # запретить DOWN

            # Exploration: случайное действие из допустимых
            if random.random() < self.exploration_rate:
                valid_actions = [a for a, m in zip(list(ActionType), action_mask) if m]
                actions.append(random.choice(valid_actions))
                continue

            # Exploitation: Q-value с маской
            start = i * len(ActionType)
            end = (i + 1) * len(ActionType)
            elevator_q_values = output[:, start:end].clone()

            # Применяем маску — недопустимые действия = -inf
            mask_tensor = torch.tensor(action_mask, dtype=torch.bool, device=self.device)
            elevator_q_values[:, ~mask_tensor] = float('-inf')

            best_action_idx = torch.argmax(elevator_q_values).item()
            actions.append(ActionType(best_action_idx))

        return actions

    def _compute_action_mask(self, manager_state, elevator_idx):
        """Вычисляет маску допустимых действий [UP, DOWN, WAIT, STOP]"""
        elevator_state = manager_state.elevators_state[elevator_idx]
        current_level = elevator_state.current_level
        max_level = len(manager_state.outside_calls) - 1

        action_mask = [True, True, True, True]

        # Границы этажей
        if current_level >= max_level:
            action_mask[0] = False  # запретить UP
        if current_level <= 0:
            action_mask[1] = False  # запретить DOWN

        # Пассажир на этаже → только STOP/WAIT
        should_stop = (
            elevator_state.going_to_level[current_level] > 0 or
            manager_state.outside_calls[current_level] > 0
        )
        if should_stop:
            action_mask[0] = False
            action_mask[1] = False

        return action_mask

    def learn(self, state, reward, action, next_state, case_info, manager_state=None, next_manager_state=None):
        # Вычисляем маску для next_state
        next_action_masks = []
        if next_manager_state is not None:
            for i in range(self.elevators):
                mask = self._compute_action_mask(next_manager_state, i)
                next_action_masks.append(mask)
        else:
            next_action_masks = [[True, True, True, True] for _ in range(self.elevators)]

        self.buffer.push(state, action, next_state, reward, next_action_masks)

        if len(self.buffer) < self.batch_size:
            return

        self.learn_step_counter += 1

        transitions = self.buffer.sample(self.batch_size)
        batch = Transition(*zip(*transitions))

        state_batch = torch.cat([self._convert_elevator_state_to_tensor(s) for s in batch.state])
        action_values = []
        for actions in batch.action:
            action_values.append([actions[i].value + len(ActionType) * i for i in range(Environment.ELEVATORS)])
        action_batch = torch.tensor(action_values, dtype=torch.int64).to(self.device)
        reward_batch = torch.tensor(batch.reward, dtype=torch.float32).to(self.device)
        if reward_batch.dim() == 1:
            reward_batch = reward_batch.unsqueeze(1)
        next_state_batch = torch.cat([self._convert_elevator_state_to_tensor(s) for s in batch.next_state])

        # Преобразуем маски в тензор [batch_size, elevators, 4]
        next_masks_batch = torch.tensor(batch.next_action_mask, dtype=torch.bool, device=self.device)

        q_predicted = self.forward(state_batch)
        q_predicted_actions = q_predicted.gather(1, action_batch).squeeze()

        # Используем TARGET NETWORK для Q(s', a') С МАСКОЙ
        with torch.no_grad():
            q_next = self._forward_target(next_state_batch)
        q_target = reward_batch + self.gamma * self._process_q_values_masked(q_next, next_masks_batch)

        loss = self.loss_function(q_predicted_actions, q_target.squeeze())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Периодически обновляем target network
        if self.learn_step_counter % self.target_update_freq == 0:
            self._update_target_network()

        if case_info.step % 1000 == 0:
            wandb.log({
                'case_test_number': case_info.case,
                'episode': case_info.episode,
                'step': case_info.step,
                'loss': loss.item(),
                'reward': reward_batch.mean().item(),
                'exploration_rate': self.exploration_rate,
            })

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = x.unsqueeze(1)
        x, _ = self.rnn(x)
        x = x[:, -1, :]
        x = self.dropout(x)
        x = self.fc3(x)
        return x

    @staticmethod
    def _process_q_values(q_next):
        max_q_values = []
        num_elevators = Environment.ELEVATORS
        actions_per_elevator = len(ActionType)

        for i in range(num_elevators):
            start_index = i * actions_per_elevator
            end_index = start_index + actions_per_elevator
            q_next_elevator = q_next[:, start_index:end_index]
            max_q_next_elevator = q_next_elevator.max(1)[0]
            max_q_values.append(max_q_next_elevator)

        max_q_next_combined = torch.stack(max_q_values, dim=1)

        return max_q_next_combined

    def _process_q_values_masked(self, q_next, masks):
        """
        Вычисляет max Q-value только для допустимых действий.
        masks: [batch_size, num_elevators, 4] — маска допустимых действий
        """
        max_q_values = []
        num_elevators = Environment.ELEVATORS
        actions_per_elevator = len(ActionType)

        for i in range(num_elevators):
            start_index = i * actions_per_elevator
            end_index = start_index + actions_per_elevator
            q_next_elevator = q_next[:, start_index:end_index].clone()

            # Применяем маску для этого лифта
            elevator_mask = masks[:, i, :]  # [batch_size, 4]
            q_next_elevator[~elevator_mask] = float('-inf')

            max_q_next_elevator = q_next_elevator.max(1)[0]
            max_q_values.append(max_q_next_elevator)

        max_q_next_combined = torch.stack(max_q_values, dim=1)

        return max_q_next_combined

    def _convert_elevator_state_to_tensor(self, state):
        state = [item for sublist in state for item in (sublist if isinstance(sublist, list) else [sublist])]
        state = torch.tensor(state, dtype=torch.float32).to(self.device)
        state = state.unsqueeze(0)
        return state

    def refresh_state(self):
        pass
