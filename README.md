# Dynamic Pathfinding Agent

This project implements a grid-based Dynamic Pathfinding Agent using Python and Pygame. It leverages Informed Search Algorithms (A* and Greedy Best-First Search) to navigate from a fixed Start Node to a Goal Node. In **Dynamic Mode**, obstacles can spawn randomly while the agent is in transit, triggering real-time collision detection and re-planning.

## Features
- **Interactive Configuration**: Initial GUI to select Grid Size, Algorithm, Heuristic, Map Density, and Dynamic Mode.
- **Algorithms**: A* Search and Greedy Best-First Search (GBFS).
- **Heuristics**: Manhattan Distance and Euclidean Distance.
- **Dynamic Mode**: Obstacles spawn with a given probability while the agent moves along the calculated path. If an obstacle blocks the current path, the agent re-calculates an optimal route to the goal from its current position.
- **Real-Time Visualization**:
  - **Yellow**: Frontier Nodes (Open Set)
  - **Red**: Visited Nodes (Closed Set)
  - **Green**: Optimal Path
  - **Purple**: Agent's current transit position
  - **Black**: Obstacles (Walls)
  - **Orange**: Start Node
  - **Turquoise**: Goal Node
- **Metrics Dashboard**: Displays current Algorithm, Node selection, Path Cost, and Execution Time in milliseconds.

## Installation Instructions

1. Ensure you have Python installed (Python 3.x recommended).
2. Install the required dependency, `pygame`:
   ```bash
   pip install pygame
   ```
3. `tkinter` is built-in with standard Python distributions.

## How to Run

1. Open a terminal or command prompt in the project directory.
2. Run the main script:
   ```bash
   python main.py
   ```
3. A configuration menu will appear. Select your desired settings and click **Start Simulation**.

## Controls
- **Left Mouse Click (LMB)**: Place the Start Node (1st click), Goal Node (2nd click), and draw Walls/Obstacles.
- **Right Mouse Click (RMB)**: Remove a Node (Walls, Start, or Goal).
- **C Key**: Clear the board completely.
- **R Key**: Generate a random maze (based on configuration density). Requires both Start and Goal nodes to be placed first.
- **SPACEBAR**: Start the search algorithm.
