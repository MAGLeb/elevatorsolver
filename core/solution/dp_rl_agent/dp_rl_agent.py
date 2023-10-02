import torch
import torch.nn as nn
import torch.optim as optim

from core.solution.agent import Agent


class ElevatorNet(nn.Module, Agent):
    def __init__(self, levels, learning_rate=0.001):
        super(ElevatorNet, self).__init__(levels)

        self.fc1 = nn.Linear(levels * 2 + 3, 1024)
        self.fc2 = nn.Linear(1024, 1024)
        self.fc3 = nn.Linear(1024, 5)

        self.relu = nn.LeakyReLU()
        self.loss_function = nn.MSELoss()
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        self.gamma = 0.99

    def choose_action(self, state):
        pass

    def save(self):
        pass

    def learn(self):
        pass

    def reset_exploration_rate(self):
        pass

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)

    def compute_loss(self, batch):
        states, actions, rewards, next_states = zip(*batch)

        states = torch.stack(states)
        next_states = torch.stack(next_states)
        rewards = torch.Tensor(rewards)
        actions = torch.LongTensor(actions)

        Q_predicted = self(states)
        Q_predicted_actions = Q_predicted.gather(1, actions.unsqueeze(1)).squeeze()

        Q_next = self(next_states).detach()
        Q_target = rewards + self.gamma * Q_next.max(1)[0]

        loss = self.loss_function(Q_predicted_actions, Q_target)

        return loss

    def train_step(self, batch):
        loss = self.compute_loss(batch)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()


# Пример использования:
model = ElevatorNet()
batch = [(torch.rand(22), 2, 1.0, torch.rand(22)) for _ in range(32)]  # Примерный батч
loss_value = model.train_step(batch)
print(f"Loss: {loss_value}")
