# crossroads_simulation
Crossroad simulation for PPC project 

# Crossroads Simulation Project

## Overview
This project simulates a multi-process system for managing traffic at a crossroads using Python. The simulation handles normal and high-priority traffic, coordinating vehicle movements through message queues, signals, shared memory, and sockets. It visualizes real-time traffic flow and light states.

## Project Structure

```
crossroads_simulation/
├── main.py                 # Main entry point of the simulation
├── traffic/
│   ├── __init__.py         # Package initializer
│   ├── normal_traffic.py   # Normal traffic generation logic
│   ├── priority_traffic.py # Priority traffic generation logic
│   ├── coordinator.py      # Manages traffic flow
│   ├── lights.py           # Traffic light management
│   ├── display.py          # Real-time visualization
├── utils/
│   ├── __init__.py         # Package initializer
│   ├── shared_memory.py    # Shared memory management
│   ├── message_queues.py   # Message queue operations
│   ├── signals.py          # Signal handling for priority vehicles
├── tests/                  # Unit tests for each component
│   ├── test_normal.py
│   ├── test_priority.py
│   ├── test_coordinator.py
│   ├── test_lights.py
│   ├── test_display.py
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation (this file)
```

## Key Components

### 1. **Coordinator**
The coordinator is the central process that:
- Dequeues vehicles from message queues.
- Determines if vehicles can pass based on the light state.
- Gives priority to high-priority vehicles by notifying the lights process.
- Updates shared memory to reflect the current state of the intersection.

### 2. **Sockets**
Sockets are used for communication between the `coordinator` and the `display` process. The `coordinator` sends real-time updates to the `display`, including:
- Traffic light states.
- Vehicles at the intersection.

**Example of Socket Use:**
The `display` process listens for updates on a predefined port and visualizes:
- Current light states (e.g., `GREEN_N-S`, `RED_W-E`).
- Vehicle positions and movements.

### 3. **Traffic Processes**
- `normal_traffic_gen`: Generates normal vehicles and enqueues them.
- `priority_traffic_gen`: Generates high-priority vehicles and sends signals for immediate light changes.

### 4. **Lights Process**
Manages traffic light states:
- Cycles lights between `GREEN` and `RED` in normal operation.
- Overrides light states for high-priority vehicles.

### 5. **Display Process**
Visualizes the intersection state using data received from the `coordinator` via sockets.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the simulation:
   ```bash
   python main.py
   ```

## Useful Git Commands During Development

- **Check the Status of Your Repository**
  ```bash
  git status
  ```

- **Commit Changes**
  ```bash
  git add .
  git commit -m "Add feature X or update structure"
  ```

- **Push Changes to Remote**
  ```bash
  git push origin main
  ```

- **Create and Switch to a New Branch for Features**
  ```bash
  git checkout -b feature/<feature_name>
  ```

- **Merge Branch into Main**
  ```bash
  git checkout main
  git merge feature/<feature_name>
  ```

