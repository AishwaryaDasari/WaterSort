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

**Build and test each component in this sequence. Do not move to the next step until the current one passes.**

### Why This Order?

- `state.py` has no dependencies — build it first
- `moves.py` depends only on `state.py`
- `heuristic.py` depends only on `state.py`
- `solver.py` depends on all three above
- `printer.py` is independent (output only)
- `main.py` wires everything together

### Implementation Sequence

1. **`state.py`** — data structure, canonical form, goal detection
2. **`moves.py`** — move generation, pour computation, pruning
3. **`heuristic.py`** — fragmentation score, transition score
4. **`solver.py`** — A* search loop
5. **`printer.py`** — formatted output
6. **`main.py`** — wiring everything together

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

**Complexity:** O(1) to create, O(n) to hash where n = number of tubes

### Canonical Form

Sort the outer tuple before any comparison or storage. This treats boards with the same tubes in different positions as the same state.

```python
def canonical(state):
    return tuple(sorted(state))
```

**Complexity:** O(n log n) where n = number of tubes. This is called on every state insertion into visited set.

**Bottleneck at scale:** For puzzles with 20+ tubes, canonical form computation becomes significant. Consider caching or hash-based alternatives for very large puzzles.

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

**Complexity:** O(n × m) where n = tubes, m = capacity. Called once per state when popped from heap.

### Complete Tube Check

Used by move pruning in `moves.py`.

```python
def is_complete(tube, capacity):
    return len(tube) == capacity and len(set(tube)) == 1
```

**Complexity:** O(m) where m = tube capacity

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

**Complexity:** O(n × m) where n = number of tubes, m = average layers per tube

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

**Complexity:** O(n × m) where n = number of tubes, m = average layers per tube

### Combined Heuristic

```python
def heuristic(state):
    return fragmentation_score(state) + transition_score(state)
```

**Complexity:** O(n × m) — both components scan all layers once

---

### Admissibility Proof

**Theorem:** h(state) = fragmentation_score(state) + transition_score(state) never overestimates the actual moves needed to reach the goal.

**Proof:**

**Part 1: Fragmentation score is admissible**

Let C be a color appearing in k distinct tubes. To consolidate C into one tube requires moving it from k-1 tubes into a single destination. Each pour operation can:
- Move C from one tube to another
- Reduce the tube count for C by at most 1

Therefore, minimum pours needed for C ≥ (k - 1).

Fragmentation score for C = (k - 1), so fragmentation_score(C) ≤ actual moves for C.

Summing across all colors: each color's fragmentation is an independent lower bound. The pours that consolidate color A are distinct from pours that consolidate color B (they move different layers). Therefore:

```
Σ fragmentation(C) ≤ Σ actual_moves(C) ≤ total_moves
```

**Part 2: Transition score is admissible**

A transition is a position in a tube where layer[i] ≠ layer[i+1]. Each transition represents a misplaced layer that must eventually be separated.

Each pour operation can:
- Remove layers from the top of a tube
- Eliminate at most 1 transition (the one at the top of the source tube)

If a tube has t transitions, it requires at least t pours to resolve them all (one transition eliminated per pour, best case).

Therefore: transition_score ≤ actual moves needed.

**Part 3: Their sum is admissible**

Key insight: fragmentation and transitions measure different aspects of remaining work.

- Fragmentation counts how many consolidation operations are needed (moving colors between tubes)
- Transitions count how many separation operations are needed (removing misplaced layers)

A single pour can improve both simultaneously:
- Pouring 2×R from tube A to tube B reduces fragmentation for R by 1 (one fewer tube contains R)
- The same pour eliminates the transition at the top of tube A

Because one pour can satisfy both constraints, the sum never exceeds the actual work:

```
h(state) = frag + trans ≤ actual_moves
```

**Concrete Example:**

```
State: T0:[R,B,R]  T1:[R]  T2:[]

Fragmentation for R: appears in 2 tubes → score = 1
Transitions in T0: R→B (1), B→R (1) → score = 2
h(state) = 1 + 2 = 3

Actual solution:
  Move 1: T0→T2  (1×R)     → T0:[R,B]  T1:[R]  T2:[R]
  Move 2: T0→T1  (1×B)     → T0:[R]    T1:[R,B]  T2:[R]
  Move 3: T0→T2  (1×R)     → T0:[]     T1:[R,B]  T2:[R,R]
  (suboptimal path shown for illustration)

Optimal solution: 2 moves
  Move 1: T0→T2  (1×R)     → eliminates 1 transition, reduces R fragmentation
  Move 2: T0→T1  (1×B)     → eliminates 1 transition
  (R consolidation happens naturally)

h(state) = 3, actual = 2, but we need ≥ 2 moves, so h is admissible (doesn't overestimate).
```

The heuristic may underestimate (h < actual) but never overestimates (h > actual). This guarantees A* finds optimal solutions.

---

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

**Complexity:**
- Time: O(b^d) worst case, where b = branching factor (~n²), d = solution depth
- Space: O(states_explored) for visited dict + O(frontier_size) for heap
- In practice: A* with good heuristic explores O(d) to O(d²) states for Water Sort

**Bottlenecks:**
- `canonical()` called twice per state (at pop and at push) — O(n log n) each
- `heuristic()` called once per generated state — O(n × m)
- Heap operations — O(log k) where k = heap size

### Why visited is checked at pop, not at push

States are pushed with their estimated f-value at generation time. By the time a state is popped, a cheaper path to it may have already been found and processed. Checking at pop — and skipping if already in visited — correctly handles this without needing to update existing heap entries, which Python's heapq does not support efficiently.

**Concrete Example:**

```
Initial state: T0:[R,B]  T1:[B,R]  T2:[]

Step 1: Pop initial state, generate children:
  - Child A: T0→T2 (cost g=1, h=2, f=3)
  - Child B: T1→T2 (cost g=1, h=2, f=3)
  Both pushed to heap.

Step 2: Pop Child A (f=3), generate its children:
  - Child C: T1→T0 (cost g=2, h=1, f=3)
  - Child D: T1→T2 (cost g=2, h=0, f=2) ← This is the same state as Child B but via different path!
  
Step 3: Pop Child D (f=2) — this is the goal, found via A→D path (cost 2)

Step 4: Later, Child B (f=3) is popped, but visited check sees it was already processed at cost 1.
  If we had checked at push and rejected Child D, we would have missed the cheaper path.
```

The key: a state can be reached via multiple paths. We want the cheapest path. Checking at pop ensures we process each state only once, at its cheapest cost.

**Why not update heap entries?** Python's heapq doesn't support decrease-key efficiently. Checking at pop is simpler and correct.

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

## Unit Testing Strategy

### Test Each Component Independently

Create a `tests/` directory with one test file per module:

```
tests/
    test_state.py
    test_moves.py
    test_heuristic.py
    test_solver.py
```

### Example: test_state.py

```python
import pytest
from state import canonical, is_goal, is_complete

def test_canonical_sorts_tubes():
    s1 = (('R', 'B'), ('G', 'Y'))
    s2 = (('G', 'Y'), ('R', 'B'))
    assert canonical(s1) == canonical(s2)

def test_goal_detection_empty_tubes():
    state = (('R', 'R'), ('B', 'B'), ())
    assert is_goal(state, capacity=2) == True

def test_goal_detection_partial_fill():
    state = (('R',), ('B', 'B'), ())
    assert is_goal(state, capacity=2) == False

def test_complete_tube_uniform():
    assert is_complete(('R', 'R', 'R'), capacity=3) == True

def test_complete_tube_mixed():
    assert is_complete(('R', 'B', 'R'), capacity=3) == False
```

### Example: test_heuristic.py

```python
import pytest
from heuristic import heuristic, fragmentation_score, transition_score

def test_heuristic_zero_on_goal():
    goal = (('R', 'R', 'R'), ('B', 'B', 'B'), ())
    assert heuristic(goal) == 0

def test_fragmentation_single_tube():
    state = (('R', 'R'), ('B', 'B'), ())
    assert fragmentation_score(state) == 0

def test_fragmentation_split_color():
    state = (('R',), ('R',), ('B', 'B'), ())
    assert fragmentation_score(state) == 1  # R in 2 tubes

def test_transition_uniform_tube():
    state = (('R', 'R', 'R'),)
    assert transition_score(state) == 0

def test_transition_mixed_tube():
    state = (('R', 'B', 'R'),)
    assert transition_score(state) == 2  # R→B and B→R
```

### Example: test_solver.py (Integration)

```python
import pytest
from solver import solve

def test_trivial_puzzle():
    state = (('R', 'B'), ('B', 'R'), ())
    path = solve(state, capacity=2)
    assert path is not None
    assert len(path) == 4

def test_baseline_puzzle():
    state = (
        ('R', 'B', 'G', 'Y'),
        ('G', 'R', 'Y', 'B'),
        ('Y', 'G', 'B', 'R'),
        ('B', 'Y', 'R', 'G'),
        (),
    )
    path = solve(state, capacity=4)
    assert path is not None
    assert len(path) == 13

def test_already_solved():
    state = (('R', 'R'), ('B', 'B'), ())
    path = solve(state, capacity=2)
    assert path == []

def test_unsolvable_no_empty():
    state = (('R', 'B'), ('B', 'R'))
    path = solve(state, capacity=2)
    assert path is None
```

### Running Tests

```bash
# Install pytest
uv add --dev pytest

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_heuristic.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv add --dev pytest-cov
uv run pytest --cov=. --cov-report=html
```

### Test-Driven Development Flow

1. Write test for component (it fails)
2. Implement component (test passes)
3. Refactor if needed (test still passes)
4. Move to next component

This ensures each piece works before integration.

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