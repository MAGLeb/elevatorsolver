import random
from collections import namedtuple, deque

import torch
import torch.nn as nn
import torch.optim as optim

from core.agent.agent import Agent
from core.types.action_type import ActionType

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
    def __init__(self, learning_rate=0.0001, exploration_rate=1, buffer_size=45000, batch_size=64):
        nn.Module.__init__(self)
        Agent.__init__(self)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.buffer = ReplayBuffer(buffer_size)
        self.batch_size = batch_size

        self.fc1 = nn.Linear(self.levels * 2 + 3, 512)
        self.fc2 = nn.Linear(512, 5)

        self.relu = nn.LeakyReLU()
        self.loss_function = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        self.gamma = 0.99
        self.exploration_rate = exploration_rate

        self.to(self.device)

    def load(self, filepath):
        checkpoint = torch.load(filepath)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    def save(self, filepath):
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filepath)

    def choose_action(self, state) -> ActionType:
        self.exploration_rate *= self.exploration_fall
        random_action = random.random()
        if random_action < self.exploration_rate:
            return random.choice(list(ActionType))

        state = self._convert_elevator_state_to_tensor(state)
        output = self.forward(state)
        best_action = torch.argmax(output).item()
        return ActionType(best_action)

    def learn(self, state, reward, action, next_state):
        self.buffer.push(state, action, next_state, reward)

        if len(self.buffer) < self.batch_size:
            return

        transitions = self.buffer.sample(self.batch_size)
        batch = Transition(*zip(*transitions))

        state_batch = torch.cat([self._convert_elevator_state_to_tensor(s) for s in batch.state])
        action_values = [a.value for a in batch.action]
        action_batch = torch.tensor(action_values, dtype=torch.int64).view(-1, 1)
        reward_batch = torch.tensor(batch.reward, dtype=torch.float32).view(-1, 1)
        next_state_batch = torch.cat([self._convert_elevator_state_to_tensor(s) for s in batch.next_state])

        q_predicted = self.forward(state_batch)
        q_predicted_actions = q_predicted.gather(1, action_batch).squeeze()

        q_next = self.forward(next_state_batch).detach()
        q_target = reward_batch + self.gamma * q_next.max(1)[0].unsqueeze(1)

        loss = self.loss_function(q_predicted_actions, q_target.squeeze())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def _convert_elevator_state_to_tensor(self, state):
        state = [item for sublist in state for item in (sublist if isinstance(sublist, list) else [sublist])]
        state = torch.tensor(state, dtype=torch.float32).to(self.device)
        state = state.unsqueeze(0)
        return state

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)
