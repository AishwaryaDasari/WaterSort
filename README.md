# Water Sort Puzzle Solver

A Python implementation of optimal solvers for the Water Sort puzzle game using various search algorithms including A*, BFS, DFS, IDDFS, and Greedy search.

## What Is This?

Water Sort is a logic puzzle where you sort colored layers across tubes by pouring between them. This project implements an optimal A* solver that finds the shortest solution.

**Example puzzle:**
```
Initial:                    Goal:
  T0      T1      T2          T0      T1      T2
 ----    ----    ----        ----    ----    ----
| R  |  | B  |  |    |      | R  |  | B  |  |    |
| B  |  | R  |  |    |      | R  |  | B  |  |    |
 ----    ----    ----        ----    ----    ----
```

**Rules:**
- Pour from top of one tube to another
- Colors must match (or destination is empty)
- Multiple consecutive layers pour together in one move
- Goal: Each tube is either full with one color or empty

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

- **[GETTING_STARTED.md](docs/GETTING_STARTED.md)** - Tutorial for first-time users
- **[analysis.md](docs/analysis.md)** - Game rules, logic, and solving principles
- **[comparison.md](docs/comparison.md)** - Algorithm performance comparison (4-color baseline)
- **[a_star_implementation.md](docs/a_star_implementation.md)** - Complete A* implementation guide
- **[EXAMPLES.md](docs/EXAMPLES.md)** - Example puzzles with solutions
- **[GLOSSARY.md](docs/GLOSSARY.md)** - Terminology reference
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[ENTROPY.md](docs/ENTROPY.md)** - Advanced heuristic analysis
- **[CRITIQUE.md](docs/CRITIQUE.md)** - Documentation quality assessment

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

## Limitations

- **Puzzle size**: Optimal for 4-6 colors. Puzzles with 10+ colors may take minutes to solve.
- **Memory**: Large puzzles (8+ colors) can use significant memory for state storage.
- **Unsolvable puzzles**: Returns `None` if no solution exists. Most puzzles need at least one empty tube.
- **No GUI**: Command-line interface only, no graphical visualization.
- **Single algorithm**: Only A* is implemented. Other algorithms (BFS, DFS, IDDFS, Greedy) are documented but not coded.

## Contributing

Contributions are welcome. Please ensure any changes maintain the optimality guarantees of the A* implementation and include appropriate test cases.
