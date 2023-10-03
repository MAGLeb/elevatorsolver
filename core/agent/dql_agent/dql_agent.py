import random

import torch
import torch.nn as nn
import torch.optim as optim

from core.agent.agent import Agent
from core.agent.utils import calculate_exploration_fall
from core.utils.environment import Environment
from core.types.action_type import ActionType


class LearningAgentDQL(nn.Module, Agent):
    def __init__(self, levels, learning_rate=0.001, exploration_rate=1):
        super().__init__(levels)

        self.fc1 = nn.Linear(levels * 2 + 3, 1024)
        self.fc2 = nn.Linear(1024, 1024)
        self.fc3 = nn.Linear(1024, 5)

        self.relu = nn.LeakyReLU()
        self.loss_function = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        self.gamma = 0.99
        self.exploration_rate = exploration_rate
        self.exploration_fall = calculate_exploration_fall(Environment.MAX_STEPS)

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
            return ActionType(random.randint(0, ActionType.__len__() - 1))

        state = self._convert_elevator_state_to_tensor(state)
        output = self.forward(state)
        best_action = torch.argmax(output).item()
        return ActionType(best_action)

    def learn(self, state, reward, action, next_state):
        state = self._convert_elevator_state_to_tensor(state)
        next_state = self._convert_elevator_state_to_tensor(next_state)
        reward = torch.tensor([reward])
        action = torch.tensor([action])

        q_predicted = self.forward(state)
        q_predicted_actions = q_predicted.gather(1, action.unsqueeze(1)).squeeze()

        q_next = self.forward(next_state).detach()
        q_target = reward + self.gamma * q_next.max(1)[0]

        loss = self.loss_function(q_predicted_actions, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def reset_exploration_rate(self):
        self.exploration_rate = 1

    @staticmethod
    def _convert_elevator_state_to_tensor(state):
        state = [item for sublist in state for item in (sublist if isinstance(sublist, list) else [sublist])]
        state = torch.tensor(state, dtype=torch.float32)
        state = state.unsqueeze(0)
        return state

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)
