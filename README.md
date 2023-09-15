# Elevator Problem with RF Agents

In this repository, we focus on utilizing Reinforcement Learning (RF) agents to solve the elevator problem. We explore different algorithms to train our agents, providing a rich environment for experimentation and learning.

![Elevator Visualization](/unity/Recordings/readme.gif)

#### Visualization Legend:
- **Red**: Represents an outside call.
- **Blue**: Represents an inside call.
- **Magenta**: Used when both inside and outside calls are present.

Please note that the visualization does not depict individual humans, however, in the code, multiple humans can exist on the same level. Each human is assigned a specific weight, and the elevator has a defined `MAX_weight` that it can carry.


## Features

### Core Training Environment
A foundational framework to generate various tests for training models with different parameters.

### Unity Visualization
Interactive visualization built in Unity that communicates with the Python backend. Witness the training in real-time or dive deep into the results to understand agent behavior.

### Baseline Model
A naive approach that surprisingly provides commendable results. Use this as a starting point to understand the problem before diving into more complex algorithms.

### Q-Table Algorithm
Dive deeper with the Q-Table algorithm, exploring how a tabular approach can be used to optimize the agent's decisions in the elevator problem.

## Getting Started

### 1. **Clone the Repository**
git clone https://github.com/your_username/elevator_rf_agents.git
cd elevator_solver

### 2. Set Up the Environment
- pip3 install -r requirements.txt
- create the **.env** (see the .env.example)
- modify **environment.py** (/elevator_solver/core/utils/environment.py) to set up the expiriment

### 3. Train the Model
python3 train.py

### 4. Validate the Model
python3 train.py

### 5. Visualize the resulted model
python3 server.py (start Falsk serveer to send action to Unity visualisation)
start Unity project (/elevator_solver/unity/)

### 6. Contributions
Feel free to contribute to the project. Raise an issue or submit a pull request.

## Roadmap
- [X] Baseline Model
- [X] Q-Table Algorithm
- [ ] Deep Q-Network Implementation
- [ ] Policy Gradient Methods
- [ ] Further Integration with Unity for Advanced Visualizations

## License
This project is licensed under the MIT License. See the LICENSE file for details.
