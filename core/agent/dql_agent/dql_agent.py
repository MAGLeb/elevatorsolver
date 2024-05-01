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

Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))


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
    def __init__(self, learning_rate=0.0001, exploration_rate=1, buffer_size=4500, batch_size=64):
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

        self.to(self.device)
        self.log_model_params()

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
        self.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    def save(self, filepath):
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filepath)

    def choose_action(self, state) -> List[ActionType]:
        actions = []

        self.exploration_rate *= self.exploration_fall
        random_action = random.random()
        if random_action < self.exploration_rate:
            for i in range(self.elevators):
                actions.append(random.choice(list(ActionType)))
            return actions

        state = self._convert_elevator_state_to_tensor(state)
        output = self.forward(state)
        for i in range(self.elevators):
            start = i * len(ActionType)
            end = (i + 1) * len(ActionType)
            elevator_actions = output[:, start:end]

            best_actions = torch.argmax(elevator_actions).item()
            actions.append(ActionType(best_actions))

        return actions

    def learn(self, state, reward, action, next_state, case_info):
        self.buffer.push(state, action, next_state, reward)

        if len(self.buffer) < self.buffer_size:
            return

        transitions = self.buffer.sample(self.batch_size)
        batch = Transition(*zip(*transitions))

        state_batch = torch.cat([self._convert_elevator_state_to_tensor(s) for s in batch.state])
        action_values = []
        for actions in batch.action:
            action_values.append([actions[i].value + len(ActionType) * i for i in range(Environment.ELEVATORS)])
        action_batch = torch.tensor(action_values, dtype=torch.int64)
        reward_batch = torch.tensor(batch.reward, dtype=torch.float32)
        next_state_batch = torch.cat([self._convert_elevator_state_to_tensor(s) for s in batch.next_state])

        q_predicted = self.forward(state_batch)
        q_predicted_actions = q_predicted.gather(1, action_batch).squeeze()

        q_next = self.forward(next_state_batch).detach()
        q_target = reward_batch + self.gamma * self._process_q_values(q_next)

        loss = self.loss_function(q_predicted_actions, q_target.squeeze())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if case_info.step % 1000 == 0:
            wandb.log({
                'case_test_number': case_info.case,
                'episode': case_info.episode,
                'step': case_info.step,
                'loss': loss.item(),
                'reward': reward_batch.mean().item(),
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

    def _convert_elevator_state_to_tensor(self, state):
        state = [item for sublist in state for item in (sublist if isinstance(sublist, list) else [sublist])]
        state = torch.tensor(state, dtype=torch.float32).to(self.device)
        state = state.unsqueeze(0)
        return state
