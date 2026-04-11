# Getting Started with Water Sort Solver

## What is Water Sort?

Water Sort is a logic puzzle where you sort colored layers across tubes by pouring between them. Here's a simple example:

```
Initial State:              Goal State:
  T0      T1      T2          T0      T1      T2
 ----    ----    ----        ----    ----    ----
| R  |  | B  |  |    |      | R  |  | B  |  |    |
| B  |  | R  |  |    |      | R  |  | B  |  |    |
 ----    ----    ----        ----    ----    ----
```

You can only pour from the top of one tube to another, and colors must match (or the destination must be empty).

## Quick Start

### 1. Install Dependencies

First, install `uv` if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
git clone https://gitlab.com/pavani_23/watersort.git
cd watersort
uv sync
```

### 3. Run the Solver

```bash
uv run python main.py
```

You'll see output like this:

```
Initial state:
  T0: ['R', 'B', 'G', 'Y']
  T1: ['G', 'R', 'Y', 'B']
  T2: ['Y', 'G', 'B', 'R']
  T3: ['B', 'Y', 'R', 'G']
  T4: []

Move 1: T0 → T4  (pour 1×Y)
  T0: ['R', 'B', 'G']
  T1: ['G', 'R', 'Y', 'B']
  ...

────────────────────────────────────────
Solved in 13 moves.
```

## Customizing Puzzles

Edit `main.py` to solve your own puzzles:

```python
TUBE_CAPACITY = 4

INITIAL_STATE = (
    ('R', 'B', 'G', 'Y'),  # Tube 0 (bottom to top)
    ('G', 'R', 'Y', 'B'),  # Tube 1
    ('Y', 'G', 'B', 'R'),  # Tube 2
    ('B', 'Y', 'R', 'G'),  # Tube 3
    (),                     # Tube 4 (empty)
)
```

### Rules for Valid Puzzles:

1. Each color must appear exactly `TUBE_CAPACITY` times total
2. Include at least one empty tube (most puzzles need this)
3. Use single-character strings for colors: 'R', 'G', 'B', 'Y', etc.
4. Tubes are written bottom-to-top

### Example: Simple 2-Color Puzzle

```python
TUBE_CAPACITY = 2

INITIAL_STATE = (
    ('R', 'B'),
    ('B', 'R'),
    (),
)
```

This should solve in 4 moves.

## Understanding the Output

Each move shows:
- **Move number**: Sequential count
- **Source → Destination**: Which tubes (T0, T1, etc.)
- **Pour quantity**: How many layers moved (e.g., "2×R" means 2 red layers)
- **Resulting state**: All tubes after the move

### Multi-Layer Pours

The solver correctly handles pouring multiple consecutive layers in one move:

```
Before:              After:
  T0      T1           T0      T1
 ----    ----          ----    ----
| R  |  | R  |        | B  |  | R  |
| R  |  |    |   →    |    |  | R  |
| B  |  |    |        |    |  | R  |
 ----    ----          ----    ----

Move: T0 → T1  (pour 2×R)
```

## What Algorithm Does It Use?

By default, the solver uses **A*** (A-star), which:
- Guarantees the shortest solution (optimal)
- Is very efficient (explores ~14 states for a 4-color puzzle)
- Works well up to ~10 colors

Other algorithms (BFS, DFS, IDDFS, Greedy) are available but not implemented by default. See [comparison.md](docs/comparison.md) for details.

## Common Issues

### "No solution found"

Your puzzle might be unsolvable. Check:
- Does each color appear exactly `TUBE_CAPACITY` times?
- Is there at least one empty tube?

Example of unsolvable puzzle:
```python
# No empty tube - circular dependency
INITIAL_STATE = (
    ('R', 'B'),
    ('B', 'R'),
)
```

### "Takes too long"

Large puzzles (8+ colors) can take time. Expected performance:
- 4 colors: < 1 second
- 6 colors: ~1 second
- 8 colors: ~10 seconds
- 10+ colors: may take minutes

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more help.

## Next Steps

- **Learn the rules**: Read [analysis.md](docs/analysis.md) for complete game logic
- **See more examples**: Check [EXAMPLES.md](docs/EXAMPLES.md) for 10+ puzzles
- **Understand the algorithm**: Read [a_star_implementation.md](docs/a_star_implementation.md)
- **Compare algorithms**: See [comparison.md](docs/comparison.md) for performance data
- **Build your own**: Follow the implementation guide to create your own solver

## FAQ

**Q: Can I use this as a Python library?**  
A: Currently it's a command-line tool only. You can import the functions, but there's no formal API.

**Q: Does it have a graphical interface?**  
A: No, it's command-line only. Output is text-based.

**Q: Can it solve any Water Sort puzzle?**  
A: It can solve any solvable puzzle, but very large ones (15+ colors) may be slow.

**Q: How do I know if my puzzle is solvable?**  
A: If the solver returns `None`, the puzzle is unsolvable. Most puzzles with at least one empty tube are solvable.

**Q: Can I change the algorithm?**  
A: Yes, but you'll need to implement other algorithms yourself. The codebase is structured to make this easy. See the implementation guide.

**Q: Why A* instead of BFS?**  
A: A* finds optimal solutions much faster. For a 4-color puzzle, A* explores ~14 states while BFS explores ~66 states.
