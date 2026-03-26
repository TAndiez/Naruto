import torch
import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AI.Agents.dqn_agent import DQNAgent
import matplotlib.pyplot as plt
import config
import pygame 
from env import Environment
from Data.Game.Bot.action import ACTION_LIST
MATCH_TIME = [20000, 30000, 90000]
def evaluate(env: "Environment", phase = 1, checkpoint_path="AI/checkpoints/checkpoint_phase_1.pth"):
    state_dim = len(env.get_state(phase=phase))
    action_dim = len(ACTION_LIST)
    agent = DQNAgent(state_dim, action_dim, phase)
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    agent.model.load_state_dict(checkpoint["model_state"])
    agent.target_model.load_state_dict(checkpoint["target_state"])
    agent.optimizer.load_state_dict(checkpoint["optimizer_state"])
    agent.epsilon = checkpoint["epsilon"]
    while True:
        state = env.reset(phase=phase)
        start_time = pygame.time.get_ticks()
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            if env.game_over():
                break
            # time-based termination
            if pygame.time.get_ticks() - start_time >= MATCH_TIME[phase - 1]:
                    break
            action_idx = agent.choose_action(state)
            state = env.get_state(phase=phase)
            actions = ACTION_LIST[action_idx]
            env.demo(actions, phase=phase)
            env.clock.tick(config.FPS / 2)


def plot(path, phase: int = 1):
    episodes = []
    rewards = []
    epsilons = []

    # Regex match đúng format log
    pattern = re.compile(
        r"Phase\s+(\d+),\s*Episode\s+(\d+),\s*Total Reward:\s*([-0-9.]+),\s*Epsilon:\s*([0-9.]+)"
    )

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.search(line)
            if not match:
                print("Skipping invalid line:", line.strip())
                continue

            episode = int(match.group(2))
            reward = float(match.group(3))
            epsilon = float(match.group(4))

            episodes.append(episode)
            rewards.append(reward)
            epsilons.append(epsilon)

    save_dir = "AI/Evaluation"
    os.makedirs(save_dir, exist_ok=True)

    plt.figure()
    plt.plot(episodes, rewards)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.title(f"Phase {phase}: Reward per Episode")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"reward_plot_{phase}.png"))
    plt.show()

    plt.figure()
    plt.plot(episodes, epsilons)
    plt.xlabel("Episode")
    plt.ylabel("Epsilon")
    plt.title(f"Phase {phase}:Epsilon per Episode")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"epsilon_plot_{phase}.png")) 
    plt.show()

if __name__ == "__main__":
    phase = 1
    log_path = f"AI/logs/training_log_phase_{phase}.txt"
    model_path = f"AI/checkpoints/checkpoint_phase_{phase}.pth"
    evaluate_env = Environment(render_mode=True, volume=0)
    evaluate(evaluate_env, phase=phase, checkpoint_path=model_path)
