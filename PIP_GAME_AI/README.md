# Naruto AI – Reinforcement Learning Project

This project implements a **2D fighting game environment inspired by the Naruto universe**, combined with a **Deep Q-Network (DQN)** agent trained using **Curriculum Learning**.  
The goal is to develop an AI agent capable of learning effective combat strategies through progressive training stages.

---

## 📌 Project Overview

- Custom 2D fighting game environment built with **Pygame**
- Reinforcement Learning agent based on **Deep Q-Network (DQN)**
- Curriculum Learning strategy to stabilize and accelerate training
- Pre-trained model checkpoints provided for demonstration and evaluation

---

## 🛠️ Technologies

- **Python 3.10**
- **PyTorch** – Deep Q-Network implementation
- **Pygame** – Game environment and rendering
- **NumPy**

---

## ⚙️ Setup & Installation

### Requirements
- Python **3.10** (recommended)
- GPU: required
### Install source
```bash
git clone https://github.com/Susantoco/PIP_GAME_AI.git
```
### Install dependencies
```bash
pip install -r requirements.txt
```
### Run Game
```bash
python main.py
```

### Test the AI Agent

- Step 1: Download pre-trained checkpoints
```bash
python download_checkpoints.py
```
- Step 2: Test the DQN agent
```bash
python AI/evaluate.py
```
## 📊 Results & Demonstration
A demonstration of the trained agent is available at: "https://drive.google.com/drive/folders/16_Jb_NoGaqCCpZpquZAsQgeOL-Jof1Wu"

## 📁 Project Structure
```bash
project/
├── AI/
│   ├── Agents/
│   │   └── dqn_agent.py
│   ├── Memory/
│   │   └── replay_buffer.py
│   ├── checkpoints/
│   ├── logs/
│   ├── Evaluation/
│   ├── env.py
│   ├── train.py
│   ├── evaluate.py
│   └── utils.py
│
├── Data/
│   └── Game/
│       ├── Bot/
│       ├── Player/
│       ├── game.py
│       ├── character.py
│       ├── skill.py
│       ├── map.py
│       └── effect.py
│
├── API/
│   ├── Interface/
│   ├── Images/
│   └── Music/
│
├── config.py
├── main.py
└── setup.py
```
## 📄 License
This project is intended for educational and research purposes only.
## ✨ Acknowledgements
- Inspired by the Naruto universe
- Reinforcement Learning concepts based on Deep Q-Network (DQN) research
