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
- git clone https://github.com/your_username/elevator_rf_agents.git
- cd elevator_solver

### 2. Set Up the Environment
- pip3 install -r requirements.txt
- create the **.env** (see the .env.example)
- modify **environment.py** (/elevator_solver/core/utils/environment.py) to set up the expiriment

### 3. Generate tests, train & validate the Model
- python3 generate_cases.py
- python3 train.py
- python3 validate.py

### 4. Visualize the resulted model
- python3 server.py (start Falsk serveer to send action to Unity visualisation)
- start Unity project (/elevator_solver/unity/)

### 5. Contributions
- Feel free to contribute to the project. Raise an issue or submit a pull request.

## Reward System

### Actions
| Action | Value | Description |
|--------|-------|-------------|
| UP     | 0     | Move elevator one floor up |
| DOWN   | 1     | Move elevator one floor down |
| WAIT   | 2     | Stay in place (do nothing) |
| STOP   | 3     | Stop and service passengers (open/close doors) |

### Rewards

#### Passenger Rewards
| Reward | Value | Description |
|--------|-------|-------------|
| GET_PASSENGER | +2.0 | Taking a passenger into elevator |
| DELIVER_PASSENGER | +10.0 | Delivering passenger to destination |
| FAST_DELIVERY_BONUS | 0 to +2.0 | Bonus for fast delivery (formula: `2.0 × (1 - wait_time / levels)` if `wait_time ≤ levels`) |

#### Energy Costs
| Reward | Value | Description |
|--------|-------|-------------|
| ENERGY_MOVE | -0.01 | Cost of movement (UP/DOWN) |
| ENERGY_IDLE | 0 | Cost of staying in place |

#### Behavior Penalties
| Reward | Value | Condition |
|--------|-------|-----------|
| MOVE_TO_EDGE | -1.0 | Attempting to move beyond floor boundaries |
| IDLE_WITH_CALLS | -1.0 | Choosing WAIT when there are active calls |
| MOVE_WITHOUT_PURPOSE | -1.0 | Moving (UP/DOWN) when there are no calls |
| MISSED_STOP | -1.0 | Passing by a passenger (UP/DOWN instead of STOP) **only if elevator is not full** |

#### STOP Action Rewards
| Reward | Value | Description |
|--------|-------|-------------|
| SUCCESSFUL_STOP | +0.5 | Stopping where there are passengers |
| USELESS_STOP | -1.0 | Stopping where there are no passengers |

#### Per-Step Penalties (Accumulating)
| Reward | Value | Description |
|--------|-------|-------------|
| WAITING_PASSENGER_PENALTY | -0.1 | Per waiting passenger per step (creates pressure to pick up) |
| PASSENGER_INSIDE_PENALTY | -0.05 | Per passenger inside elevator per step (creates pressure to deliver) |

### Potential-Based Reward Shaping (Training Only)

To solve the sparse reward problem, we use **potential-based reward shaping**:

```
shaping_reward = γ × φ(s') - φ(s)
```

Where:
- `γ = 0.99` (discount factor)
- `φ(s)` = potential of state = negative sum of distances to all active calls

**Potential calculation:**
```python
potential = 0
# External calls (weight 1.0)
for level, has_call in enumerate(outside_calls):
    if has_call:
        potential -= abs(level - current_level)

# Internal passengers (weight 4.0 - priority!)
for level, going in enumerate(going_to_level):
    if going:
        potential -= 4.0 * abs(level - current_level)
```

**Example:**
- Elevator at floor 0, call at floor 4
- φ(s) = -4 (distance 4)
- Move UP → φ(s') = -3 (distance 3)
- Shaping reward = 0.99 × (-3) - (-4) = +1.03

This gives **immediate positive reward** for moving towards goals!

**Important:** Shaping is applied only during training, not during validation.

## Roadmap
- [X] Baseline Model
- [X] Q-Table Algorithm
- [X] Deep Q-Network Implementation
- [ ] Policy Gradient Methods
- [ ] Further Integration with Unity for Advanced Visualizations
