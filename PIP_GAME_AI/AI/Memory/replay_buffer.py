import random
from collections import deque
CAPACITY = [50000, 200000, 1000000]
class ReplayBuffer:
    """Simple replay buffer for DQN"""
    def __init__(self, capacity=1000000):
        self.max_size = capacity
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def merge(self, other_buffer):
        if other_buffer is None or len(other_buffer.buffer) == 0:
            return

        old_list = list(other_buffer.buffer)
        self.buffer = deque(old_list, maxlen=self.max_size)

    def __len__(self):
        return len(self.buffer)
