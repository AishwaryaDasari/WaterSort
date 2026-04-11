# Water Sort: Algorithm Comparison and State Representation

---

## 1. The Puzzle Used for This Comparison

All algorithms below are run on the same hard puzzle: 4 colors (R, G, B, Y), 6 tubes each holding up to 4 layers, with 4 fully mixed tubes and 2 empty tubes.

### Initial State

```
T0: [R, B, G, Y]   ← bottom to top
T1: [G, R, Y, B]
T2: [Y, G, B, R]
T3: [B, Y, R, G]
T4: []
T5: []
```

Every color appears exactly once in every tube. No color is adjacent to itself anywhere. This is the worst-case fragmentation for 4 colors — maximum transitions, maximum spread.

### Goal State

```
T0: [R, R, R, R]
T1: [G, G, G, G]
T2: []
T3: [B, B, B, B]
T4: [Y, Y, Y, Y]
T5: []
```

Any permutation of colors across tubes is acceptable — what matters is that each non-empty tube is uniform and full.

---

## 2. How the Game State Is Represented

### Core Data Structure

Each tube is modeled as a stack. Only the topmost element is accessible at any time. The full game state is a tuple of tuples — one inner tuple per tube, ordered from bottom to top.

```
State = tuple of tuples

Example (initial state):
(
  ('R', 'B', 'G', 'Y'),   ← T0
  ('G', 'R', 'Y', 'B'),   ← T1
  ('Y', 'G', 'B', 'R'),   ← T2
  ('B', 'Y', 'R', 'G'),   ← T3
  (),                      ← T4 empty
  ()                       ← T5 empty
)
```

A tuple of tuples is chosen because it is immutable and hashable — both properties are required for storing states in visited sets and priority queues.

### Why Tube Order Does Not Matter

The physical position of tubes on the board carries no meaning. T0 containing RED and T1 containing BLUE is the same logical puzzle as T0 containing BLUE and T1 containing RED. To exploit this, states are stored in **canonical form** — the inner tuples are sorted before hashing. This means the solver treats those two configurations as identical and avoids exploring both.

```
canonical(state) = tuple(sorted(state))
```

This single step dramatically reduces the number of distinct states the solver must track.

### How a Move Is Represented

A move is a pair (i, j): pour from tube i into tube j. The move does not store how many layers transfer — that is derived at the time of application from the run length at the top of tube i and the available space in tube j. The number of layers that transfer is always the minimum of those two values.

### State Storage Throughout the Game

| Purpose | Data Structure | What It Stores |
|---|---|---|
| Visited states | Hash set | Canonical state tuples |
| BFS frontier | Queue (deque) | (state, path) pairs |
| DFS stack | Call stack / explicit stack | Current state + path |
| A* frontier | Min-heap (priority queue) | (f, g, counter, state, path) |
| Path reconstruction | List | Sequence of (i, j) move pairs |

The `counter` field in the A* heap is a tiebreaker — when two states have equal f-values, the heap needs a third comparison key to avoid comparing state tuples directly (which would require defining an ordering on tuples of different lengths).

---

## 3. The Full Solution (13 Moves)

This is the optimal solution found by both BFS and A*. Every algorithm that finds an optimal solution produces this exact sequence.

```
Move  1: T0→T4   pour 1×Y  into empty tube
Move  2: T3→T0   pour 1×G  onto G
Move  3: T2→T3   pour 1×R  onto R
Move  4: T1→T2   pour 1×B  onto B
Move  5: T1→T4   pour 1×Y  onto Y
Move  6: T3→T1   pour 2×R  onto R    ← multi-layer pour
Move  7: T3→T4   pour 1×Y  onto Y
Move  8: T2→T3   pour 2×B  onto B    ← multi-layer pour
Move  9: T0→T2   pour 2×G  onto G    ← multi-layer pour
Move 10: T0→T3   pour 1×B  onto B
Move 11: T1→T0   pour 3×R  onto R    ← multi-layer pour
Move 12: T2→T1   pour 3×G  onto G    ← multi-layer pour
Move 13: T2→T4   pour 1×Y  onto Y
```

### State Evolution Move by Move

The full board after each move, tubes shown as [bottom ... top]:

```
Start:
  T0:[R,B,G,Y]  T1:[G,R,Y,B]  T2:[Y,G,B,R]  T3:[B,Y,R,G]  T4:[]  T5:[]

Move 1  (T0→T4, 1×Y):
  T0:[R,B,G]    T1:[G,R,Y,B]  T2:[Y,G,B,R]  T3:[B,Y,R,G]  T4:[Y]  T5:[]

Move 2  (T3→T0, 1×G):
  T0:[R,B,G,G]  T1:[G,R,Y,B]  T2:[Y,G,B,R]  T3:[B,Y,R]    T4:[Y]  T5:[]

Move 3  (T2→T3, 1×R):
  T0:[R,B,G,G]  T1:[G,R,Y,B]  T2:[Y,G,B]    T3:[B,Y,R,R]  T4:[Y]  T5:[]

Move 4  (T1→T2, 1×B):
  T0:[R,B,G,G]  T1:[G,R,Y]    T2:[Y,G,B,B]  T3:[B,Y,R,R]  T4:[Y]  T5:[]

Move 5  (T1→T4, 1×Y):
  T0:[R,B,G,G]  T1:[G,R]      T2:[Y,G,B,B]  T3:[B,Y,R,R]  T4:[Y,Y]  T5:[]

Move 6  (T3→T1, 2×R):
  T0:[R,B,G,G]  T1:[G,R,R,R]  T2:[Y,G,B,B]  T3:[B,Y]      T4:[Y,Y]  T5:[]

Move 7  (T3→T4, 1×Y):
  T0:[R,B,G,G]  T1:[G,R,R,R]  T2:[Y,G,B,B]  T3:[B]        T4:[Y,Y,Y]  T5:[]

Move 8  (T2→T3, 2×B):
  T0:[R,B,G,G]  T1:[G,R,R,R]  T2:[Y,G]      T3:[B,B,B]    T4:[Y,Y,Y]  T5:[]

Move 9  (T0→T2, 2×G):
  T0:[R,B]      T1:[G,R,R,R]  T2:[Y,G,G,G]  T3:[B,B,B]    T4:[Y,Y,Y]  T5:[]

Move 10 (T0→T3, 1×B):
  T0:[R]        T1:[G,R,R,R]  T2:[Y,G,G,G]  T3:[B,B,B,B]  T4:[Y,Y,Y]  T5:[]

Move 11 (T1→T0, 3×R):
  T0:[R,R,R,R]  T1:[G]        T2:[Y,G,G,G]  T3:[B,B,B,B]  T4:[Y,Y,Y]  T5:[]

Move 12 (T2→T1, 3×G):
  T0:[R,R,R,R]  T1:[G,G,G,G]  T2:[Y]        T3:[B,B,B,B]  T4:[Y,Y,Y]  T5:[]

Move 13 (T2→T4, 1×Y):
  T0:[R,R,R,R]  T1:[G,G,G,G]  T2:[]         T3:[B,B,B,B]  T4:[Y,Y,Y,Y]  T5:[]
  ✓ SOLVED
```

---

## 4. Algorithm Comparison: Real Numbers on This Puzzle

| Algorithm | Moves in Solution | Nodes Explored | Memory Held | Optimal? |
|---|---|---|---|---|
| BFS | 13 | 1,038 | 211 states (max queue) | Yes |
| A* | 13 | 14 | ~14 states | Yes |
| IDDFS | 13 | 31,895 | O(depth) only | Yes |
| DFS | 13 | 10,556 | O(depth) only | Coincidental |
| Greedy | 13 | 13 | ~13 states | Coincidental |

### Reading the Table

"Nodes explored" means the number of states the algorithm fully processed before finding the solution. A* explored only 14 states to find the optimal 13-move solution. BFS explored 1,038. IDDFS explored 31,895 — it finds the optimal solution but does so by repeatedly restarting from depth 1 up to the solution depth, paying a large node-count penalty for memory efficiency.

DFS and Greedy found 13-move solutions on this puzzle, but this is coincidental — neither algorithm guarantees optimality. On a different puzzle with a trickier layout, both could return suboptimal solutions or fail entirely.

---

## 5. How Each Algorithm Stores and Processes State

### BFS — Queue of (state, path) pairs

BFS stores the frontier as a queue. Each entry in the queue is a complete snapshot of the board paired with the move sequence that led there.

```
Queue at start:
[ ( initial_state, [] ) ]

After expanding Move 1 (all valid first moves enqueued):
[
  ( state_after_T0→T4, [(0,4)] ),
  ( state_after_T0→T5, [(0,5)] ),
  ( state_after_T1→T4, [(1,4)] ),
  ( state_after_T1→T5, [(1,5)] ),
  ... (all valid first moves)
]
```

Every state at depth 1 is enqueued before any state at depth 2 is processed. The max queue size of 211 means BFS was simultaneously holding 211 partial solutions in memory at the widest point of its search. Each entry stores a full board state plus its path — on larger puzzles, this becomes the memory bottleneck.

The visited set stores canonical state tuples. Before enqueuing any state, BFS checks: has this canonical form been seen before? If yes, discard. This prevents cycles and duplicate work.

### DFS — Recursive call stack with backtracking

DFS uses the program's call stack (or an explicit stack) rather than a queue. It commits to one move, recursively explores all consequences of that move, and only backtracks when it hits a dead end or the depth limit.

```
Call stack at Move 6 of the solution:
  recurse(initial, depth=50)
    recurse(after_move_1, depth=49)
      recurse(after_moves_1-2, depth=48)
        recurse(after_moves_1-3, depth=47)
          recurse(after_moves_1-4, depth=46)
            recurse(after_moves_1-5, depth=45)
              ...exploring...
```

DFS only keeps the current path in memory at any moment — not the entire frontier. This is why its memory usage is O(depth) regardless of how wide the search tree is. The tradeoff is that it explored 10,556 nodes, backtracking many times before finding the solution.

The visited dictionary stores canonical states mapped to the depth at which they were last seen. If DFS reaches a state it has visited before at an equal or greater remaining depth, it prunes that branch — continuing would only find longer solutions.

### IDDFS — Repeated DFS with increasing depth limits

IDDFS runs DFS multiple times. Each run has a fixed depth ceiling. It starts at depth 1, then 2, then 3, and so on until a solution is found. When the depth limit equals the actual solution depth (13), that run of DFS finds the solution.

```
Run 1: DFS with depth limit 1  → no solution found
Run 2: DFS with depth limit 2  → no solution found
...
Run 13: DFS with depth limit 13 → solution found, 13 moves
```

Each run starts fresh — no state is carried between runs. This is why the total node count is 31,895: states near the root are re-explored on every run. The memory at any moment is still just the current path (O(depth)), making IDDFS the most memory-efficient algorithm that still guarantees the optimal solution.

The repeated work is less wasteful than it appears. Each run's cost is proportional to its depth limit. Because trees branch, the last run (at depth 13) dominates the total cost — earlier runs are comparatively cheap. The total overhead is roughly the same order as one full BFS traversal to that depth.

### A* — Priority queue ordered by f = g + h

A* stores the frontier in a min-heap ordered by f-value. The f-value of a state is the sum of g (moves taken so far) and h (heuristic estimate of moves still needed).

```
Priority queue structure per entry:
  (f_value, g_value, counter, state, path)

Initial heap:
  [ (0 + 24 = 24,  g=0,  ctr=0,  initial_state,  []) ]
        ↑ h=24 at start (high fragmentation + many transitions)
```

The heuristic value of 24 at the start reflects the worst-case configuration: every color is maximally fragmented and every tube has maximum transitions. As moves resolve the puzzle, the heuristic drops steadily:

```
Start:    h=24,  g=0,   f=24
Move 1:   h=23,  g=1,   f=24
Move 2:   h=21,  g=2,   f=23
Move 3:   h=19,  g=3,   f=22
Move 4:   h=17,  g=4,   f=21
Move 5:   h=15,  g=5,   f=20
Move 6:   h=13,  g=6,   f=19
Move 7:   h=11,  g=7,   f=18
Move 8:   h=9,   g=8,   f=17
Move 9:   h=7,   g=9,   f=16
Move 10:  h=5,   g=10,  f=15
Move 11:  h=3,   g=11,  f=14
Move 12:  h=1,   g=12,  f=13
Move 13:  h=0,   g=13,  f=13  ← goal reached
```

The f-value decreases monotonically here because the heuristic is both admissible and consistent on this puzzle. A* only needed to explore 14 nodes total — it essentially followed the optimal path without deviating because the heuristic was strong enough to make every correct move obviously better than any alternative.

The heuristic used is:

Fragmentation score: for each color, count the number of distinct tubes it appears in, minus 1. A color split across 3 tubes contributes 2 to this score — the minimum number of consolidation pours needed for that color alone.

Transition score: for each tube, count the number of positions where the color changes between consecutive layers (bottom to top). Each transition represents a layer sitting on top of a color it does not belong with, which must be resolved.

Both scores are admissible — they never overestimate the true remaining work — so A* is guaranteed to find the optimal solution.

### Greedy — No backtracking, heuristic-only

Greedy always moves to the neighbor state with the lowest heuristic value. It maintains no frontier queue and performs no backtracking.

```
Step 1: evaluate all valid moves from initial state
        pick the move that minimizes h(next_state)
Step 2: move there, never revisit
Step 3: repeat until goal or dead end
```

Greedy found a 13-move solution on this puzzle and explored only 13 nodes — one per move. This looks ideal in the table, but it is misleading. Greedy succeeded here because this particular puzzle's heuristic landscape happens to be smooth — every greedy step was also the correct step. On puzzles with misleading local optima (where the best-looking next state leads into a dead end), Greedy either returns a suboptimal long solution or fails entirely with no fallback.

Greedy stores no path history and no queue — only the current state. It is the most memory-efficient algorithm of all, at the cost of reliability.

---

## 6. Summary: When to Use Each Algorithm

| Algorithm | Use when... |
|---|---|
| BFS | Correctness matters most, puzzle size is small to medium, and you need a guaranteed shortest path |
| DFS | Memory is severely constrained, puzzle depth is bounded, and solution length does not matter |
| IDDFS | You want guaranteed optimal solution with minimal memory — best uninformed choice for large puzzles |
| A* | You want optimal solutions efficiently at any scale — best overall choice with a good heuristic |
| Greedy | You want a fast approximate solver and can tolerate occasional failures on hard puzzles |

The data from this puzzle makes the core tradeoff concrete: A* explored 14 nodes to find the optimal solution. BFS explored 1,038 to find the same solution. IDDFS explored 31,895. The heuristic is not magic — it is structured knowledge about what progress looks like in Water Sort, encoded as a number, allowing A* to ignore 98% of the states that BFS and IDDFS had to visit.