# Water Sort Puzzle Solver

A Python implementation of optimal solvers for the Water Sort puzzle game using various search algorithms including A*, BFS, DFS, IDDFS, and Greedy search.

## What Is This?

Water Sort is a logic puzzle where you sort colored layers across tubes by pouring between them. This project implements multiple algorithms to find optimal solutions, with A* being the most efficient approach.

This is a command-line solver with no graphical interface.

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) for package management

## Installation

Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and set up the project:

```bash
git clone https://gitlab.com/pavani_23/watersort.git
cd watersort
uv sync
```

## Usage

Run the solver on a puzzle configuration:

```bash
uv run python main.py
```

The solver will output each move and the resulting board state, finishing with the total move count.

## Project Structure

```
watersort/
├── main.py          # Entry point and puzzle configuration
├── state.py         # State representation and goal checking
├── moves.py         # Move generation and validation
├── heuristic.py     # A* heuristic functions
├── solver.py        # A* search implementation
├── printer.py       # Console output formatting
└── docs/            # Detailed documentation
```

## Documentation

Comprehensive technical documentation is available in the `docs/` directory:

- **[analysis.md](docs/analysis.md)** - Game rules, logic, and solving principles
- **[comparision.md](docs/comparision.md)** - Algorithm performance comparison with real data
- **[a_star_implementation.md](docs/a_star_implementation.md)** - Complete A* implementation guide

## Algorithm Performance

Tested on a 4-color, 6-tube puzzle with maximum fragmentation:

| Algorithm | Moves | Nodes Explored | Optimal? |
|-----------|-------|----------------|----------|
| A*        | 13    | 14             | Yes      |
| BFS       | 13    | 1,038          | Yes      |
| IDDFS     | 13    | 31,895         | Yes      |
| DFS       | 13    | 10,556         | No*      |
| Greedy    | 13    | 13             | No*      |

*DFS and Greedy found optimal solutions on this puzzle by coincidence but don't guarantee optimality.

## Key Features

- **Optimal solutions** - A* guarantees minimum move count
- **Multi-layer pours** - Correctly handles pouring multiple consecutive layers in one move
- **State deduplication** - Canonical form reduces explored states by ~50%
- **Move pruning** - Eliminates redundant moves (empty-to-empty, complete sources, etc.)
- **Admissible heuristic** - Fragmentation + transition scoring never overestimates

## How It Works

The solver represents each tube as a stack and the full game as a tuple of tuples. A* explores states using a priority queue ordered by f = g + h, where:

- **g** = moves taken so far
- **h** = estimated moves remaining (fragmentation score + transition count)

The heuristic guides A* to explore only ~14 states for puzzles that BFS would explore 1,000+ states to solve.

## Customizing Puzzles

Edit the puzzle configuration in `main.py`:

```python
TUBE_CAPACITY = 4

INITIAL_STATE = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    (),  # empty tube
    (),  # empty tube
)
```

Colors can be any single-character string. Tubes are represented bottom-to-top.

## Development

This project uses **uv** for dependency management. To add dependencies:

```bash
uv add <package-name>
```

To run in development mode:

```bash
uv run python main.py
```

## License

This project is open source. See individual files for details.

## Contributing

Contributions are welcome. Please ensure any changes maintain the optimality guarantees of the A* implementation and include appropriate test cases.
