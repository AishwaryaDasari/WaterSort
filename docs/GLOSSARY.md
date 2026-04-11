# Glossary

## Core Concepts

**State** - A complete snapshot of all tubes and their contents at a given moment. Represented as a tuple of tuples.

**Canonical form** - A normalized state representation where tubes are sorted. Ensures equivalent states (same tubes in different positions) are treated identically.

**Move** - A pour operation from source tube to destination tube, represented as a pair (i, j).

**Run length** - The number of consecutive matching layers at the top of a tube.

**Pour quantity** - The number of layers transferred in a single move: min(run_length, available_space).

## State Properties

**Complete tube** - A tube filled to capacity with a single uniform color.

**Empty tube** - A tube containing zero layers.

**Goal state** - A state where every tube is either complete or empty.

**Fragmentation** - The degree to which colors are scattered across multiple tubes.

**Transition** - A position in a tube where adjacent layers have different colors.

## Algorithm Terms

**Admissible heuristic** - A heuristic function that never overestimates the actual cost to reach the goal.

**Consistent heuristic** - A heuristic where h(n) ≤ cost(n, n') + h(n') for any successor n'.

**Visited set** - A collection of previously explored states, used to prevent cycles.

**Frontier** - The set of states waiting to be explored (queue for BFS, heap for A*, stack for DFS).

**Node** - A state in the search tree. "Nodes explored" counts how many states were fully processed.

**Branching factor** - The average number of valid moves from any given state.

## Heuristic Components

**Fragmentation score** - For each color, count the number of distinct tubes it appears in, minus 1. Sum across all colors.

**Transition score** - For each tube, count positions where the color changes between adjacent layers. Sum across all tubes.

## Move Types

**Consolidation move** - A move that reduces fragmentation by gathering a color into fewer tubes.

**Separation move** - A move that resolves a transition by removing a misplaced layer.

**Deadlock** - A state from which no sequence of moves can reach the goal.

**Pruned move** - A legal move that is skipped because it produces no progress (e.g., empty-to-empty).

## Performance Metrics

**Solution length** - The number of moves in the returned path.

**Nodes explored** - The number of states fully processed before finding the solution.

**Max states in memory** - Peak memory usage measured in number of states stored simultaneously.

**Optimal solution** - The shortest possible path from initial state to goal.
