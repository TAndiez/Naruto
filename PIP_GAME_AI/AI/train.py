import numpy as np
import torch
import pygame
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import config
from Agents.dqn_agent import DQNAgent
from Memory.replay_buffer import ReplayBuffer
from env import Environment
from Data.Game.Bot.action import ACTION_LIST
from utils import save_checkpoint, load_checkpoint, load_replay_buffer

EPISODES = [500, 1000, 5000]
MATCH_TIME = [20000, 30000, 90000]
PHASES = [1, 2, 3]
UPDATE_NETWORK = [20, 40, 200]
BATCH_SIZE = [256, 512, 512]
RATIO = [1, 0.5, 0.5, 0.5]
def train(env: "Environment", episodes=EPISODES, batch_size=BATCH_SIZE, match_time=MATCH_TIME, upd_nw=UPDATE_NETWORK):

    for phase in PHASES:
        # ========= Initialize Agent =========
        state_dim = len(env.get_state(phase=phase))
        action_dim = len(ACTION_LIST)
        agent = DQNAgent(state_dim, action_dim, phase)
        memory = ReplayBuffer()
        
        # ========= Load checkpoint (safe) =========
        start_episode, memory = load_checkpoint(agent, memory, phase)
        
        print(f"\n===== Starting Phase {phase} =====")
        print("\nParameter: Episode = ", episodes[phase - 1], ", Match time = ", match_time[phase-1], ", Batch size = ", batch_size[phase-1] )

        # ========= Load previous phase model =========
        if phase > 1:
            if start_episode == 0: 
                prev_mem = load_replay_buffer(phase, ratio=RATIO[phase-1])
                if prev_mem is not None:
                    memory.merge(prev_mem)
                print(f"Lenght Memory {phase}: ", len(memory.buffer))

                prev_model_path = f"AI/checkpoints/checkpoint_phase_{phase - 1}.pth"

                if os.path.exists(prev_model_path):
                    print(f"[INFO] Loading previous phase model:", prev_model_path)
                    ckpt = torch.load(prev_model_path, map_location="cpu")
                    agent.model.load_state_dict(ckpt["model_state"])
                    agent.update_target_network()

        # ========= Training =========
        for ep in range(start_episode + 1, episodes[phase - 1] + 1):
            state = env.reset(phase=phase)
            total_reward = 0
            start_time = pygame.time.get_ticks()
            done = False

            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                if env.game_over():
                    done = True
                    next_state, reward, done, _ = env.end_step(phase=phase)
                    memory.push(state, 0, reward, next_state, done)
                    total_reward += reward
                    break
                # time-based termination
                if pygame.time.get_ticks() - start_time >= match_time[phase - 1]:
                    break

                # Choose action
                action_idx = agent.choose_action(state)
                actions = ACTION_LIST[action_idx]

                # Step
                next_state, reward, done, _ = env.step(actions, phase=phase)

                # Add experience
                memory.push(state, action_idx, reward, next_state, done)

                # Train
                agent.train_step(memory, batch_size=batch_size[phase - 1])

                state = next_state
                total_reward += reward

                env.clock.tick(config.FPS / 2)

            # ========= Proper final transition (terminal state) =========
            if not done:
                done = True
                next_state, reward, done, _ = env.end_step(phase=phase)
                memory.push(state, 0, reward, next_state, done)
                total_reward += reward

            if ep % upd_nw[phase - 1] == 0:
                agent.update_target_network()
            agent.decay_epsilon()

            # Log
            log_path = f"AI/logs/training_log_phase_{phase}.txt"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a") as f:
                f.write(f"Phase {phase}, Episode {ep}, Total Reward: {total_reward:.2f}, "
                        f"Epsilon: {agent.epsilon:.2f}\n")

            # Save checkpoint
            if ep % 100 == 0:
                save_checkpoint(agent, memory, ep, phase=phase)


        print(f"Phase {phase} completed.\n")

    print("Training finished for ALL phases!")


if __name__ == "__main__":
    train(env=Environment(render_mode=True, volume=0))
