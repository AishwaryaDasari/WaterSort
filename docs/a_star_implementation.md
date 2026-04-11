# Water Sort: A* Solver — Python Implementation Guide

---

## What This Builds

A command-line A* solver that:
- Accepts any puzzle configuration (any number of tubes, any capacity, any colors)
- Finds the optimal (minimum moves) solution
- Prints the full board state after every move
- Prints the total move count at the end

No interface. No animation. Pure logic and console output.

---

## Architecture

Six files, each with one responsibility:

```
water_sort_solver/
    main.py          ← entry point, puzzle input, run solver, print output
    state.py         ← state representation, goal check, canonical form
    moves.py         ← move generation, validation, pour quantity
    heuristic.py     ← fragmentation score + transition score
    solver.py        ← A* search logic
    printer.py       ← console output
```

What calls what:

```
main.py
  ├── calls solver.py (solve)
  ├── calls printer.py (print_initial, print_move, print_solution)
  └── calls moves.py (get_top_run, apply_move) — for computing pour info during output

solver.py
  ├── calls state.py (canonical, is_goal, is_complete)
  ├── calls moves.py (get_valid_moves, apply_move)
  └── calls heuristic.py (heuristic)

moves.py
  └── calls state.py (is_complete)
```

---

## Build Order

Build and test each component in this sequence. Do not move to the next step until the current one passes.

1. `state.py` — data structure, canonical form, goal detection
2. `moves.py` — move generation, pour computation, pruning
3. `heuristic.py` — fragmentation score, transition score
4. `solver.py` — A* search loop
5. `printer.py` — formatted output
6. `main.py` — wiring everything together

---

## Step 1 — State (`state.py`)

### Data Structure

A state is a tuple of tuples. Each inner tuple is one tube, ordered bottom to top. Use tuples, not lists — tuples are immutable and hashable, which is required for the visited set and heap keys.

```python
state = (
    ('R', 'B', 'G', 'Y'),   # Tube 0, bottom to top
    ('G', 'R', 'Y', 'B'),   # Tube 1
    ('Y', 'G', 'B', 'R'),   # Tube 2
    ('B', 'Y', 'R', 'G'),   # Tube 3
    (),                      # Tube 4, empty
)
```

### Canonical Form

Sort the outer tuple before any comparison or storage. This treats boards with the same tubes in different positions as the same state.

```python
def canonical(state):
    return tuple(sorted(state))
```

### Goal Detection

```python
def is_goal(state, capacity):
    for tube in state:
        if len(tube) == 0:
            continue
        if len(tube) != capacity:
            return False
        if len(set(tube)) != 1:
            return False
    return True
```

### Complete Tube Check

Used by move pruning in `moves.py`.

```python
def is_complete(tube, capacity):
    return len(tube) == capacity and len(set(tube)) == 1
```

### Test This Step

```python
# test_state.py
from state import canonical, is_goal, is_complete

capacity = 4

# Initial state is not a goal
initial = (('R','B','G','Y'), ('G','R','Y','B'), ('Y','G','B','R'), ('B','Y','R','G'), ())
assert is_goal(initial, capacity) == False

# Goal state is recognised
goal = (('R','R','R','R'), ('G','G','G','G'), (), ('B','B','B','B'), ('Y','Y','Y','Y'))
assert is_goal(goal, capacity) == True

# Partial fill is not a goal even if uniform
partial = (('R','R'), ('G','G','G','G'), (), ('B','B','B','B'), ('Y','Y','Y','Y'))
assert is_goal(partial, capacity) == False

# Canonical form treats tube-permuted boards as equal
s1 = (('R','B'), ('G','Y'))
s2 = (('G','Y'), ('R','B'))
assert canonical(s1) == canonical(s2)

print("state.py: all tests passed")
```

---

## Step 2 — Moves (`moves.py`)

### Top Run

Returns the color and run length at the top of a tube.

```python
def get_top_run(tube):
    if not tube:
        return (None, 0)
    top_color = tube[-1]
    count = 0
    for layer in reversed(tube):
        if layer == top_color:
            count += 1
        else:
            break
    return (top_color, count)
```

### Validity Check

```python
from state import is_complete

def is_valid_move(state, i, j, capacity):
    src = state[i]
    dst = state[j]
    if not src:                            # Rule 1: source not empty
        return False
    if is_complete(src, capacity):         # Rule 2: source not already complete
        return False
    if len(dst) == capacity:               # Rule 3: destination not full
        return False
    src_top, _ = get_top_run(src)
    if dst and dst[-1] != src_top:        # Rule 4: colors match or dst empty
        return False
    return True
```

### Apply Move

Never modify the existing state. Always produce a new one.

```python
def apply_move(state, i, j, capacity):
    tubes = [list(t) for t in state]
    top_color, run_len = get_top_run(tubes[i])
    available = capacity - len(tubes[j])
    pour_count = min(run_len, available)
    for _ in range(pour_count):
        tubes[i].pop()
    tubes[j].extend([top_color] * pour_count)
    return tuple(tuple(t) for t in tubes)
```

### Generate All Valid Moves (with pruning)

```python
def get_valid_moves(state, capacity):
    moves = []
    n = len(state)
    first_empty = next((k for k in range(n) if not state[k]), None)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if not is_valid_move(state, i, j, capacity):
                continue

            # Prune: redundant empty destinations
            # If destination is empty and not the first empty tube, skip —
            # pouring into any empty tube produces an equivalent state.
            if not state[j] and j != first_empty:
                continue

            # Prune: moving a uniform incomplete tube to an empty tube
            # just relocates it without making progress.
            src_top, run_len = get_top_run(state[i])
            if not state[j] and run_len == len(state[i]):
                continue

            moves.append((i, j))

    return moves
```

### Test This Step

```python
# test_moves.py
from state import canonical
from moves import get_top_run, apply_move, get_valid_moves

capacity = 4
state = (('R','B','G','Y'), ('G','R','Y','B'), ('Y','G','B','R'), ('B','Y','R','G'), ())

# get_top_run on a non-empty tube
assert get_top_run(('R', 'B', 'G', 'G')) == ('G', 2)
assert get_top_run(()) == (None, 0)

# apply_move produces correct new state (multi-layer pour)
s = (('R', 'B', 'G', 'G'), ('G', 'R'), (), (), ())
result = apply_move(s, 0, 1, capacity)
assert result[0] == ('R', 'B')           # 2× G removed
assert result[1] == ('G', 'R', 'G', 'G') # 2× G added

# Valid moves from initial state should be non-empty
moves = get_valid_moves(state, capacity)
assert len(moves) > 0

# Redundant empty tube pruning: only T4 should appear as destination (sole empty tube)
destinations_to_empty = [j for (i, j) in moves if not state[j]]
assert len(set(destinations_to_empty)) == 1  # only the one empty tube used

print("moves.py: all tests passed")
```

---

## Step 3 — Heuristic (`heuristic.py`)

The heuristic estimates remaining moves. It must never overestimate (admissible) — this guarantees A* finds the optimal solution.

### Fragmentation Score

For each color, count the number of distinct tubes it appears in, minus 1. A color consolidated in one tube contributes 0. A color in 3 tubes contributes 2.

```python
def fragmentation_score(state):
    from collections import defaultdict
    color_tubes = defaultdict(set)
    for tube_idx, tube in enumerate(state):
        for layer in tube:
            color_tubes[layer].add(tube_idx)
    return sum(len(tubes) - 1 for tubes in color_tubes.values())
```

Why admissible: each pour can reduce a color's tube count by at most 1, so fragmentation score ≤ actual pours needed for that color. Summing across colors still never overestimates, because those pours are distinct operations.

### Transition Score

For each tube, count positions where the color changes between adjacent layers.

```python
def transition_score(state):
    total = 0
    for tube in state:
        for k in range(1, len(tube)):
            if tube[k] != tube[k - 1]:
                total += 1
    return total
```

Why admissible: each transition requires at least one pour to resolve, and each pour can eliminate at most one transition. The transition count therefore never exceeds the actual work remaining.

Why their sum is still admissible: fragmentation and transition scores count different aspects of remaining work. Fragmentation counts how many colors need consolidation; transitions count how many misplaced layers need to be separated. A single pour can improve both simultaneously (e.g., consolidating layers reduces fragmentation and removes a transition), so their sum never exceeds the actual move count.

### Combined Heuristic

```python
def heuristic(state):
    return fragmentation_score(state) + transition_score(state)
```

### Test This Step

```python
# test_heuristic.py
from heuristic import heuristic, fragmentation_score, transition_score

# Heuristic on goal state must return 0
goal = (('R','R','R','R'), ('G','G','G','G'), (), ('B','B','B','B'), ('Y','Y','Y','Y'))
assert heuristic(goal) == 0

# Fragmentation: R in 2 tubes contributes 1, G in 1 tube contributes 0, B in 1 tube contributes 0 → total 1
s = (('R', 'G'), ('R', 'B'), ())
assert fragmentation_score(s) == 1

# Transition: one change in a tube
s2 = (('R', 'G'),)
assert transition_score(s2) == 1

# Transition: uniform tube
s3 = (('R', 'R', 'R'),)
assert transition_score(s3) == 0

print("heuristic.py: all tests passed")
```

---

## Step 4 — A* Solver (`solver.py`)

### Data Structures

```python
import heapq
from state import canonical, is_goal, is_complete
from moves import get_valid_moves, apply_move
from heuristic import heuristic
```

### Heap Entry Format

```
(f_value, g_value, counter, state, path)
```

The `counter` is a unique integer incremented on every push. It serves as a tiebreaker when f values are equal, preventing Python from comparing state tuples (which would raise a TypeError for tuples of different lengths).

### Algorithm

```python
def solve(initial_state, capacity):
    h0 = heuristic(initial_state)
    counter = 0
    open_set = [(h0, 0, counter, initial_state, [])]
    visited = {}

    while open_set:
        f, g, _, state, path = heapq.heappop(open_set)

        c = canonical(state)
        if c in visited:
            continue          # already processed at equal or lower cost
        visited[c] = g

        if is_goal(state, capacity):
            return path

        for (i, j) in get_valid_moves(state, capacity):
            next_state = apply_move(state, i, j, capacity)
            nc = canonical(next_state)
            ng = g + 1

            if nc not in visited:
                nh = heuristic(next_state)
                counter += 1
                heapq.heappush(open_set, (ng + nh, ng, counter, next_state, path + [(i, j)]))

    return None  # no solution exists
```

### Why visited is checked at pop, not at push

States are pushed with their estimated f-value at generation time. By the time a state is popped, a cheaper path to it may have already been found and processed. Checking at pop — and skipping if already in visited — correctly handles this without needing to update existing heap entries, which Python's heapq does not support efficiently.

### Test This Step

```python
# test_solver.py
from solver import solve

capacity = 4
initial = (('R','B','G','Y'), ('G','R','Y','B'), ('Y','G','B','R'), ('B','Y','R','G'), ())

path = solve(initial, capacity)
assert path is not None, "Solver returned None — no solution found"
assert len(path) == 13, f"Expected 13 moves, got {len(path)}"

# Simple 2-color puzzle
simple = (('R','B'), ('B','R'), ())
path2 = solve(simple, 2)
assert path2 is not None
assert len(path2) <= 4  # verify optimality

print("solver.py: all tests passed")
```

---

## Step 5 — Output (`printer.py`)

### Functions

```python
def print_initial(state):
    print("Initial state:")
    for ti, tube in enumerate(state):
        print(f"  T{ti}: {list(tube)}")
    print()


def print_move(move_number, i, j, pour_count, color, state):
    print(f"Move {move_number}: T{i} → T{j}  (pour {pour_count}×{color})")
    for ti, tube in enumerate(state):
        print(f"  T{ti}: {list(tube)}")
    print()


def print_solution(total_moves):
    print("─" * 40)
    print(f"Solved in {total_moves} moves.")
```

### Optional: Column Display

For a more visual format, display tubes as vertical columns:

```
Move 6: T3 → T1  (pour 2×R)

  T0          T1          T2
 ------      ------      ------
| G  G |    | R  R |    | B  B |
| R    |    | G    |    | G    |
| B    |    |      |    | Y    |
| R    |    |      |    |      |
 ------      ------      ------
```

Start with the simple inline format. It is correct, readable, and easy to verify. The column format can be added once the solver is confirmed working.

---

## Step 6 — Entry Point (`main.py`)

### Puzzle Definition

Define the puzzle at the top of `main.py`. `TUBE_CAPACITY` and `INITIAL_STATE` are the only values that change between puzzles.

```python
from state import canonical
from moves import get_top_run, apply_move, get_valid_moves
from solver import solve
from printer import print_initial, print_move, print_solution

TUBE_CAPACITY = 4

INITIAL_STATE = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    (),
)
```

### Main Flow

```python
def main():
    print_initial(INITIAL_STATE)

    path = solve(INITIAL_STATE, TUBE_CAPACITY)

    if path is None:
        print("No solution found.")
        return

    state = INITIAL_STATE
    for move_number, (i, j) in enumerate(path, start=1):
        top_color, run_len = get_top_run(state[i])
        available = TUBE_CAPACITY - len(state[j])
        pour_count = min(run_len, available)
        state = apply_move(state, i, j, TUBE_CAPACITY)
        print_move(move_number, i, j, pour_count, top_color, state)

    print_solution(len(path))


if __name__ == "__main__":
    main()
```

---

## Integration Testing

After wiring everything together, run these checks:

**Baseline puzzle:** The solver must return a 13-move path on the test puzzle. If it returns more than 13 moves, the heuristic is not admissible — recheck fragmentation and transition scoring. If it returns None, move generation or goal detection has a bug.

**Simple puzzle:**
```python
TUBE_CAPACITY = 2
INITIAL_STATE = (('R', 'B'), ('B', 'R'), ())
```
Expected: solved in 4 moves.

**Already-solved puzzle:**
```python
TUBE_CAPACITY = 4
INITIAL_STATE = (('R', 'R', 'R', 'R'), ('G', 'G', 'G', 'G'), ())
```
Expected: path returned is empty (0 moves). The initial state is already the goal.

**No-solution puzzle:**
```python
TUBE_CAPACITY = 2
INITIAL_STATE = (('R', 'B'), ('R', 'B'))  # No empty tube, circular dependency
```
Expected: `solve` returns `None`.

---

## Common Bugs

**State mutation.** If `apply_move` modifies the existing state instead of creating a copy, the solver corrupts visited states. Always convert to lists, modify the copies, then convert back to tuples.

**Missing counter in heap.** Without the counter as a tiebreaker, Python compares state tuples when f and g values are equal. Tuples of different lengths raise a TypeError. The counter prevents this entirely.

**Canonical check at push vs pop.** Checking canonical at push and skipping duplicates may discard a cheaper path that arrives later. Always check at pop.

**Hardcoded capacity.** If `TUBE_CAPACITY` appears anywhere other than `main.py`, the solver breaks on other puzzles. Pass capacity as a parameter through every function that needs it.

**Heuristic non-zero on goal.** If the heuristic returns anything other than 0 on a solved state, A* will keep searching past the solution. Always test `heuristic(goal_state) == 0` explicitly.

**Pour count computed incorrectly.** The pour count in the output loop in `main.py` must be computed before calling `apply_move`, because `apply_move` changes the state. Compute `pour_count` from the original state, then apply the move.

---

## Troubleshooting

**"Solver returns None"**
- Check that each color appears exactly `capacity` times in total across all tubes.
- Verify that the puzzle has at least one empty tube — most configurations are unsolvable without one.
- Run `get_valid_moves(initial_state, capacity)` and print the result. If it is empty, move generation has a bug.
- Check that `is_goal` returns `False` on the initial state and `True` on a hand-crafted goal.

**"Solution is longer than expected"**
- The heuristic is likely not admissible. Add a debug print inside `heuristic()` and verify it returns 0 on the goal state.
- Check `fragmentation_score` — it should return 0 when every color is in exactly one tube.
- Check `transition_score` — it should return 0 when every tube is uniform.

**"Solver runs for a long time without finishing"**
- Add a node-count counter inside the solve loop and print it every 1,000 pops. If it grows without bound, the visited set is not pruning correctly.
- Verify `canonical` is being used consistently — if two identical states get different canonical forms, visited-set lookups will miss and the loop will explore duplicates forever.

**"TypeError comparing states in the heap"**
- The `counter` tiebreaker is missing or not being incremented. Every `heappush` call must include a unique counter value as the third element.

**"Output move count doesn't match path length"**
- The pour count in the output is being computed after `apply_move` instead of before. Move the pour-count computation above the `apply_move` call.

---

## Expected Output for the Baseline Puzzle

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
  T2: ['Y', 'G', 'B', 'R']
  T3: ['B', 'Y', 'R', 'G']
  T4: ['Y']

... (moves 2–12 omitted for brevity)

Move 13: T2 → T4  (pour 1×Y)
  T0: ['R', 'R', 'R', 'R']
  T1: ['G', 'G', 'G', 'G']
  T2: []
  T3: ['B', 'B', 'B', 'B']
  T4: ['Y', 'Y', 'Y', 'Y']

────────────────────────────────────────
Solved in 13 moves.
```