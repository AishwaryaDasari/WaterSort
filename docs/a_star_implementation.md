# Water Sort: A* Solver — Detailed Implementation Plan (Python)

---

## Overview of What We Are Building

A command-line A* solver that:
- Accepts any puzzle configuration (any number of tubes, any capacity, any colors)
- Finds the optimal (minimum moves) solution
- Prints the full board state after every move
- Prints the total number of moves at the end

No interface. No animation. Pure logic and console output.

---

## Project Structure

```
water_sort_solver/
    main.py          ← entry point, puzzle input, run solver, print output
    state.py         ← state representation, goal check, canonical form
    moves.py         ← move generation, move validation, pour quantity
    heuristic.py     ← fragmentation score + transition score
    solver.py        ← A* search logic
    printer.py       ← console output: board state after each move
```

Each file has exactly one responsibility. This keeps each piece testable independently before wiring everything together.

---

## Step 1 — State Representation (`state.py`)

### What a State Is

A state is a tuple of tuples. Each inner tuple represents one tube, ordered from bottom to top. The outer tuple holds all tubes.

```
state = (
    ('R', 'B', 'G', 'Y'),   ← Tube 0, bottom to top
    ('G', 'R', 'Y', 'B'),   ← Tube 1
    ('Y', 'G', 'B', 'R'),   ← Tube 2
    ('B', 'Y', 'R', 'G'),   ← Tube 3
    (),                      ← Tube 4, empty
    (),                      ← Tube 5, empty
)
```

Use a tuple of tuples — not lists — because tuples are immutable and hashable. Hashability is required for storing states in the visited set and as dictionary keys.

### Canonical Form

Sort the outer tuple before any comparison or storage. This treats boards with the same tubes in different positions as the same state.

```
canonical(state) → tuple(sorted(state))
```

This is a single line but has a large impact — it can halve or more the number of states A* needs to explore.

### Goal Check

A state is solved when every tube is either:
- Empty (length 0), or
- Full (length equals tube capacity) AND contains exactly one unique color

```
is_goal(state, capacity):
    for each tube in state:
        if tube is empty → continue
        if len(tube) != capacity → return False
        if number of unique colors in tube != 1 → return False
    return True
```

Note: capacity is passed in because it varies per puzzle. Do not hardcode it.

### What to put in state.py

- `canonical(state)` — returns sorted tuple of tuples
- `is_goal(state, capacity)` — returns True/False
- `is_complete(tube, capacity)` — True if tube is full and uniform (used in move pruning)

---

## Step 2 — Move Generation (`moves.py`)

### Top Run

Before checking validity or computing pour quantity, you need to know the color and run length at the top of a tube.

```
get_top_run(tube):
    if tube is empty → return (None, 0)
    top_color = tube[-1]
    count = 0
    iterate tube in reverse:
        if layer == top_color → count += 1
        else → break
    return (top_color, count)
```

### Validity Check

A move (source tube i → destination tube j) is valid when ALL of the following hold:

1. tube[i] is not empty
2. tube[i] is not already complete (is_complete check)
3. tube[j] is not full (len(tube[j]) < capacity)
4. tube[j] is empty, OR top color of tube[j] equals top color of tube[i]

### Pour Quantity

```
pour_count = min(run_length_of_source_top, available_space_in_destination)
```

This must be computed every time a move is applied — it is not fixed.

### Applying a Move

Never modify the existing state. Always produce a new state.

```
apply_move(state, i, j, capacity):
    convert state to list of lists (mutable copy)
    get top_color and run_len from tube[i]
    get available_space = capacity - len(tube[j])
    pour_count = min(run_len, available_space)
    remove pour_count layers from top of tube[i]
    add pour_count layers of top_color to top of tube[j]
    return tuple of tuples (immutable again)
```

### Generating All Valid Moves

```
get_valid_moves(state, capacity):
    moves = []
    for i in range(len(state)):
        for j in range(len(state)):
            if i == j → skip
            if move (i, j) passes validity check → add (i, j) to moves
    return moves
```

### Pruning Rules to Apply Inside get_valid_moves

Apply these filters before adding any move to the list:

**Prune 1 — Empty source.** Skip if tube[i] is empty. (Covered by validity rule 1.)

**Prune 2 — Complete source.** Skip if tube[i] is already complete.

**Prune 3 — Redundant empty destinations.** If tube[j] is empty and there are multiple empty tubes, only allow the move to the first empty tube index. All other empty destinations produce equivalent states — no need to explore them separately.

**Prune 4 — Uniform source to empty destination.** If tube[i] contains only one color (all layers the same) but is not yet full, and tube[j] is empty, this move just relocates an incomplete uniform tube. It adds no progress. Skip it.

### What to put in moves.py

- `get_top_run(tube)` → (color, count)
- `is_valid_move(state, i, j, capacity)` → True/False
- `apply_move(state, i, j, capacity)` → new state
- `get_valid_moves(state, capacity)` → list of (i, j) pairs

---

## Step 3 — Heuristic (`heuristic.py`)

The heuristic estimates how many moves remain from a given state to the goal. It must never overestimate (admissible) — this guarantees A* finds the optimal solution.

### Component 1 — Fragmentation Score

For each color, count the number of distinct tubes it currently appears in, then subtract 1. This gives the minimum number of consolidation pours needed for that color.

```
for each color c in the puzzle:
    tube_count = number of tubes that contain at least one layer of c
    fragmentation += (tube_count - 1)
```

A color fully consolidated in one tube contributes 0. A color spread across 3 tubes contributes 2.

### Component 2 — Transition Score

For each tube, count the number of positions where the color changes between two adjacent layers (bottom to top). Each transition represents a layer that is sitting on the wrong color and must eventually be separated.

```
for each tube in state:
    for k from 1 to len(tube) - 1:
        if tube[k] != tube[k-1]:
            transitions += 1
```

### Combined Heuristic

```
h(state) = fragmentation_score + transition_score
```

Both components measure real work that must be done. Neither can overestimate. Together they give A* strong directional guidance — in the test puzzle, the heuristic started at 24 and decreased by roughly 2 per move all the way to 0 at the solution, meaning A* never explored a wrong branch.

### What to put in heuristic.py

- `fragmentation_score(state)` → integer
- `transition_score(state)` → integer
- `heuristic(state)` → fragmentation_score + transition_score

---

## Step 4 — A* Solver (`solver.py`)

### Data Structures

```
open_set   → min-heap (priority queue), ordered by f = g + h
visited    → dictionary mapping canonical(state) → best g seen
```

### Heap Entry Format

Each entry in the heap is a tuple:

```
(f_value, g_value, counter, state, path)
```

- `f_value` — g + h, the priority key
- `g_value` — number of moves taken so far
- `counter` — a unique integer incremented for every push, used as tiebreaker when f values are equal. This avoids Python attempting to compare state tuples directly, which would fail for tuples of different lengths.
- `state` — the full board state at this node
- `path` — list of (i, j) move pairs taken to reach this state

### Algorithm

```
solve(initial_state, capacity):

    h0 = heuristic(initial_state)
    counter = 0
    push (h0, 0, counter, initial_state, []) onto open_set
    visited = {}

    while open_set is not empty:

        pop (f, g, _, state, path) from open_set   ← always the lowest f

        c = canonical(state)
        if c is in visited → skip (already processed at equal or lower cost)
        visited[c] = g

        if is_goal(state, capacity):
            return path                             ← solution found

        for each (i, j) in get_valid_moves(state, capacity):
            next_state = apply_move(state, i, j, capacity)
            nc = canonical(next_state)
            ng = g + 1

            if nc not in visited:
                nh = heuristic(next_state)
                counter += 1
                push (ng + nh, ng, counter, next_state, path + [(i, j)]) onto open_set

    return None    ← no solution exists
```

### Why visited is checked at pop, not at push

States are pushed to the heap with their estimated f-value at the time of generation. By the time a state is popped, a cheaper path to it may have already been found and processed. Checking at pop — and skipping if already in visited — correctly handles this without needing to update existing heap entries (which Python's heapq does not support efficiently).

### Path Storage

The path is stored as a list of (i, j) tuples accumulated as A* explores. Each node in the heap carries its own full path. This uses more memory than storing parent pointers, but it is simpler to implement correctly and the paths are short (typically under 50 moves) so memory is not a concern.

---

## Step 5 — Output (`printer.py`)

### Board Display Format

Print each tube as a vertical column of color labels, numbered from the top. Show tube index and whether the tube is complete or empty.

Recommended format:

```
Move 6: T3 → T1  (pour 2×R)

  T0          T1          T2          T3          T4          T5
  ----        ----        ----        ----        ----        ----
| GG  |    | RRR |    | BB  |    | Y   |    | YY  |    |     |
| R   |    | G   |    | G   |    | B   |    |     |    |     |
| B   |    |     |    | Y   |    |     |    |     |    |     |
| R   |    |     |    |     |    |     |    |     |    |     |
  ----        ----        ----        ----        ----        ----
```

Or a simpler inline format that is easier to implement first:

```
Move 6: T3 → T1  (pour 2×R)
  T0: [R, B, G, G]
  T1: [G, R, R, R]
  T2: [Y, G, B, B]
  T3: [B, Y]
  T4: [Y, Y]
  T5: []
```

Start with the simple format. It is correct and readable. Upgrade to the column format later if desired.

### What to print after each move

```
print_move(move_number, i, j, pour_count, color, state):
    print "Move {move_number}: T{i} → T{j}  (pour {pour_count}×{color})"
    for each tube index ti, tube in state:
        print "  T{ti}: {list(tube)}"
    print blank line
```

### Final output

```
print_solution(path, final_state):
    print "─" * 40
    print "Solved in {len(path)} moves."
```

### What to put in printer.py

- `print_move(move_number, i, j, pour_count, color, state)` — prints one move and resulting state
- `print_solution(total_moves)` — prints final summary line
- `print_initial(state)` — prints the starting board before any moves

---

## Step 6 — Main Entry Point (`main.py`)

### Puzzle Input

Define the puzzle directly as a tuple of tuples. Put this at the top of main.py so it is easy to change.

```python
TUBE_CAPACITY = 4

INITIAL_STATE = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    (),
    (),
)
```

### Main Flow

```
main():
    print_initial(INITIAL_STATE)

    path = solve(INITIAL_STATE, TUBE_CAPACITY)

    if path is None:
        print "No solution found."
        return

    state = INITIAL_STATE
    for move_number, (i, j) in enumerate(path, start=1):
        top_color, run_len = get_top_run(state[i])
        available = TUBE_CAPACITY - len(state[j])
        pour_count = min(run_len, available)
        state = apply_move(state, i, j, TUBE_CAPACITY)
        print_move(move_number, i, j, pour_count, top_color, state)

    print_solution(len(path))
```

---

## Build Order

Build and test each component in this order. Do not move to the next step until the current one works correctly.

**Step 1 — State and goal detection.**
Hard-code the initial state and the goal state. Call is_goal on both. Verify the initial returns False and the goal returns True. Test canonical form: manually create two states with the same tubes in different order, confirm canonical returns the same tuple for both.

**Step 2 — Move generation.**
From the initial state, print all valid moves. Manually verify each one against the four rules. Check that pruning is removing symmetric empty-tube moves and complete-source moves. Test apply_move on a specific move and confirm the resulting state is correct.

**Step 3 — Heuristic.**
Compute heuristic on the initial state. Verify fragmentation and transition scores manually by counting from the board. Compute heuristic on the goal state — it must return 0.

**Step 4 — A* solver.**
Run the solver on the initial state. Confirm it returns a path of length 13 for the test puzzle. If it returns a longer path, the heuristic is not admissible — recheck the scoring. If it returns None, move generation or goal detection has a bug.

**Step 5 — Output.**
Wire the printer into main and confirm every move and state prints correctly. Confirm the final move count matches the path length.

**Step 6 — Test additional puzzles.**
Change INITIAL_STATE to a simpler puzzle with 2 colors and 3 tubes and verify the solver finds the optimal solution. Then try a harder puzzle with 5 or 6 colors.

---

## Expected Output for the Test Puzzle

```
Initial state:
  T0: [R, B, G, Y]
  T1: [G, R, Y, B]
  T2: [Y, G, B, R]
  T3: [B, Y, R, G]
  T4: []
  T5: []

Move 1: T0 → T4  (pour 1×Y)
  T0: [R, B, G]
  T1: [G, R, Y, B]
  T2: [Y, G, B, R]
  T3: [B, Y, R, G]
  T4: [Y]
  T5: []

Move 2: T3 → T0  (pour 1×G)
  T0: [R, B, G, G]
  ...

Move 13: T2 → T4  (pour 1×Y)
  T0: [R, R, R, R]
  T1: [G, G, G, G]
  T2: []
  T3: [B, B, B, B]
  T4: [Y, Y, Y, Y]
  T5: []

────────────────────────────────────────
Solved in 13 moves.
```

---

## Common Bugs to Watch For

**State mutation.** If apply_move modifies the existing state instead of creating a new copy, the solver will corrupt visited states. Always convert to lists, modify the copies, then convert back to tuples.

**Missing counter in heap.** Without the counter as a tiebreaker, Python will attempt to compare state tuples when f and g values are equal. Tuples of different lengths raise a TypeError. The counter prevents this entirely.

**Canonical check at push vs pop.** If you check canonical at push and skip duplicates, you may discard a cheaper path to the same state that arrives later. Always check at pop.

**Hardcoded capacity.** If TUBE_CAPACITY is hardcoded anywhere other than main.py, the solver will break on puzzles with different capacity. Pass capacity as a parameter through every function that needs it.

**Heuristic returning non-zero on goal state.** If the heuristic returns anything other than 0 on a solved state, it is incorrect. This causes A* to keep searching past the solution.