import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random

phase_config = {
    1: {
        "lr": 1e-4,
        "gamma": 0.99,
        "epsilon": 1.0,
        "epsilon_decay": 0.995,
        "epsilon_min": 0.10,
    },
    2: {
        "lr": 5e-5,
        "gamma": 0.995,
        "epsilon": 0.5,
        "epsilon_decay": 0.998,
        "epsilon_min": 0.05,
    },
    3: {
        "lr": 1e-5,
        "gamma": 0.999,
        "epsilon": 0.3,
        "epsilon_decay": 0.999,
        "epsilon_min": 0.01,
    }
}

class DQN(nn.Module):
    """Deep Q-Network"""
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, x):
        return self.fc(x)


class DQNAgent:
    """DQN Agent with epsilon-greedy policy"""
    def __init__(self, state_dim, action_dim, phase=1):
        self.state_dim = state_dim
        self.action_dim = action_dim

        config = phase_config.get(phase, phase_config[1])
        self.gamma = config["gamma"]
        self.epsilon = config["epsilon"]
        self.epsilon_decay = config["epsilon_decay"]
        self.epsilon_min = config["epsilon_min"]
        lr = config["lr"]

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[INFO] Using device: {self.device}")

        self.model = DQN(state_dim, action_dim).to(self.device)
        self.target_model = DQN(state_dim, action_dim).to(self.device)

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()


    def choose_action(self, state):
        """Epsilon-greedy action selection"""
        if np.random.rand() < self.epsilon:
            action_idx = random.randint(0, self.action_dim - 1)
        else:
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.model(state)
                action_idx = torch.argmax(q_values).item()
        return action_idx

    def train_step(self, memory, batch_size=128):
        """Train one step from replay buffer"""
        if len(memory) < batch_size:
            return

        batch = memory.sample(batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)

        # Q values & target
        q_values = self.model(states).gather(1, actions)
        with torch.no_grad():
            next_q_values = self.target_model(next_states).max(1, keepdim=True)[0]
            targets = rewards + (1 - dones) * self.gamma * next_q_values

        # Optimize
        loss = self.criterion(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_network(self):
        """Copy weights to target network"""
        self.target_model.load_state_dict(self.model.state_dict())

    def decay_epsilon(self):
        """Decay epsilon for exploration"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
