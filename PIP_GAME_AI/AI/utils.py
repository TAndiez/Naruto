import os
import torch
import pickle

import os
import pickle
from collections import deque

def load_replay_buffer(phase, ratio=0.5, path="AI/checkpoints"):
    if phase <= 1:
        return None

    prev_memory_path = os.path.join(path, f"replay_buffer_phase_{phase - 1}.pkl")

    if not os.path.exists(prev_memory_path):
        print(f"[PHASE {phase}] No previous replay buffer found.")
        return None

    print(f"[PHASE {phase}] Loading previous replay buffer: {prev_memory_path}")

    with open(prev_memory_path, "rb") as f:
        prev_buffer = pickle.load(f)

    if not hasattr(prev_buffer, "max_size"):
        prev_buffer.max_size = prev_buffer.buffer.maxlen

    old_list = list(prev_buffer.buffer)
    keep = int(len(old_list) * ratio)
    keep_items = old_list[-keep:]
    prev_buffer.buffer = deque(keep_items, maxlen=prev_buffer.max_size)

    print(f"[PHASE {phase}] Imported {keep} samples from previous phase.")

    return prev_buffer


def save_checkpoint(agent, memory, episode, phase=1, path="AI/checkpoints"):
    os.makedirs(path, exist_ok=True)
    
    checkpoint_path = os.path.join(path, f"checkpoint_phase_{phase}.pth")
    memory_path = os.path.join(path, f"replay_buffer_phase_{phase}.pkl")

    torch.save({
        "episode": episode,
        "model_state": agent.model.state_dict(),
        "target_state": agent.target_model.state_dict(),
        "optimizer_state": agent.optimizer.state_dict(),
        "epsilon": agent.epsilon,
    }, checkpoint_path)

    tmp = memory_path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(memory, f)
    os.replace(tmp, memory_path)   


    print(f"[PHASE {phase}] Saved checkpoint at episode {episode}")


def load_checkpoint(agent, memory, phase=1, path="AI/checkpoints"):
    checkpoint_path = os.path.join(path, f"checkpoint_phase_{phase}.pth")
    memory_path = os.path.join(path, f"replay_buffer_phase_{phase}.pkl")

    if not os.path.exists(checkpoint_path):
        print(f"[PHASE {phase}] No checkpoint found. Starting new training.")
        return 0, memory

    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    agent.model.load_state_dict(checkpoint["model_state"])
    agent.target_model.load_state_dict(checkpoint["target_state"])
    agent.optimizer.load_state_dict(checkpoint["optimizer_state"])
    agent.epsilon = checkpoint["epsilon"]
    start_episode = checkpoint["episode"]

    if os.path.exists(memory_path):
        with open(memory_path, "rb") as f:
            memory = pickle.load(f)

    print(f"[PHASE {phase}] Resumed from episode {start_episode}, epsilon={agent.epsilon:.3f}")
    return start_episode, memory

