# Water Sort: Rules and Game Logic

---

## What Is Water Sort?

Water Sort is a logic puzzle. You have a set of tubes filled with mixed color layers. The goal is to sort them so each tube contains exactly one color, filled to capacity.

Here is a simple 2-color starting position and its goal:

```
Start:                      Goal:
  T0      T1      T2          T0      T1      T2
 ----    ----    ----        ----    ----    ----
| R  |  | B  |  |    |      | B  |  | R  |  |    |
| B  |  | R  |  |    |      | B  |  | R  |  |    |
 ----    ----    ----        ----    ----    ----
```

The number of tubes, the capacity of each tube, and the number of colors vary by level. The rule system stays constant.

---

## The Game Model

Each tube holds an ordered sequence of color layers, from bottom to top. Only the top layer is accessible at any time — each tube is a stack.

A game state is a complete snapshot of all tubes and their contents. Every move takes one state and produces a new one.

---

## Rules of a Move

A move pours from a source tube into a destination tube. All of the following must hold. If any one fails, the move is illegal.

**Rule 1 — Source must not be empty.** There is nothing to pour.

```
ILLEGAL:
  T0      T1
 ----    ----
|    |  | R  |     Cannot pour from T0 — it is empty.
|    |  | B  |
 ----    ----
```

**Rule 2 — Source must not already be complete.** A complete tube holds one uniform color at full capacity. Pouring from it undoes solved work.

```
ILLEGAL:
  T0      T1
 ----    ----
| R  |  |    |     T0 is complete. Pouring from it is forbidden.
| R  |  |    |
 ----    ----
```

**Rule 3 — Destination must not be full.** At least one unit of free space is required.

```
ILLEGAL:
  T0      T1
 ----    ----
| R  |  | B  |     T1 is full. Cannot pour into it.
| B  |  | G  |
 ----    ----
```

**Rule 4 — Colors must match, or destination must be empty.** The top color of the source must equal the top color of the destination. An empty destination accepts any color.

```
LEGAL (empty destination):       LEGAL (matching tops):        ILLEGAL (mismatch):
  T0      T1                       T0      T1                    T0      T1
 ----    ----                      ----    ----                  ----    ----
| R  |  |    |                   | R  |  | B  |                | R  |  | B  |
| B  |  |    |    T0→T1 OK       | B  |  | R  |  T0→T1 OK     | B  |  | G  |  T0→T1 ILLEGAL
 ----    ----                      ----    ----                  ----    ----
                                  (both tops are R)             (R ≠ G)
```

---

## The Pour Quantity Rule

A pour is not always a single layer. All consecutive matching layers from the top of the source pour together, subject to available space in the destination.

- The number of same-color layers at the top of the source is the **run length**.
- The number of free units in the destination is the **available space**.
- Layers transferred = minimum of run length and available space.

```
Example — run length 3, available space 2:

Before:              After:
  T0      T1           T0      T1
 ----    ----          ----    ----
| R  |  |    |        | R  |  | B  |
| B  |  |    |   →    | B  |  | B  |   (2 layers of B transferred, not 3)
| B  |  | B  |        |    |  | B  |
| B  |  | B  |        |    |  | B  |
 ----    ----          ----    ----
```

This is the most commonly misunderstood mechanic. A solver that assumes single-layer transfers produces incorrect move sequences.

---

## Goal Condition

The puzzle is solved when every tube satisfies one of:

- The tube is completely empty, or
- The tube is filled entirely with one color — no gaps, no mixed layers.

A partially filled tube with matching layers does not count as solved unless it is at full capacity.

```
SOLVED:               NOT SOLVED (partial):
  T0      T1      T2    T0      T1      T2
 ----    ----    ----   ----    ----    ----
| R  |  | B  |  |    | | R  |  | B  |  |    |
| R  |  | B  |  |    | | R  |  |    |  |    |
 ----    ----    ----   ----    ----    ----
 (full)  (full) (empty) (full) (half — not solved)
```

---

## State Identity and Canonical Form

Two states are identical when every tube contains the exact same layers in the exact same order.

The physical position of tubes carries no meaning. A solver exploits this by sorting the list of tubes into a canonical order before comparing or storing states. Two boards with the same tubes in different positions are treated as one state — this significantly reduces the number of distinct states any solver must track.

```
These two boards are the SAME state:
  T0      T1             T0      T1
 ----    ----            ----    ----
| R  |  | B  |   ≡     | B  |  | R  |
| B  |  | R  |          | R  |  | B  |
 ----    ----            ----    ----
canonical([RB, BR]) = canonical([BR, RB]) = sorted → same
```

---

## Logical Principles for Solving

### Think in Layers, Not Tubes

A buried layer cannot move until everything above it is cleared. Before making any move, identify which layers are accessible (on top) and which are not.

```
  T0
 ----
| Y  |   ← accessible
| G  |   ← buried under Y
| R  |   ← buried under Y and G
 ----
To reach R, you must first move Y, then G.
```

### Trace Dependency Chains

Every buried layer creates a dependency. To reach color A, you may need to move color B first. To move B, you may need to move C. Trace the chain to its root before acting — this gives a natural sequence of moves to execute.

### Preserve Empty Tubes

Empty tubes break deadlocks. When a dependency chain has no natural resolution, an empty tube provides a temporary holding place. Never fill an empty tube without a clear plan to empty it again.

### Prioritise Color Consolidation

Every time a color is fully gathered into one complete tube, the problem shrinks. A completed tube is permanently removed from the active puzzle. Look for colors close to consolidation and resolve those first.

### Work Backwards From the Goal

The end state is always known. When stuck, ask what the board must have looked like one move before the solution. Reverse reasoning turns "what can I do?" into "what must have happened?" — a much more constrained question.

---

## Deadlock Conditions

A deadlock is a state from which no sequence of moves reaches the goal.

**Circular dependency.** Color A is trapped under B in one tube; color B is trapped under A in another tube; no empty tube is available to break the cycle.

```
DEADLOCK — circular dependency, no empty tube:
  T0      T1
 ----    ----
| A  |  | B  |
| B  |  | A  |
 ----    ----
A cannot move onto A (B is in the way in T1).
B cannot move onto B (A is in the way in T0).
Neither can move.
```

**Space exhaustion.** Every tube is either full or topped with a color that has no valid destination.

```
DEADLOCK — space exhaustion (capacity 2):
  T0      T1      T2
 ----    ----    ----
| R  |  | B  |  | G  |
| B  |  | G  |  | R  |
 ----    ----    ----
All tubes full. No move is possible anywhere.
```

A solver should detect developing deadlocks two or three moves before they fully form, and prune those branches early.

---

## Puzzle Difficulty

These factors make a puzzle harder:

- **More colors** — more dependency chains to trace simultaneously.
- **Higher fragmentation** — a color split across many tubes requires many consolidation moves.
- **Fewer empty tubes** — less room to break deadlocks. Zero empty tubes is usually unsolvable.
- **Deeply buried target layers** — long dependency chains before any consolidation is possible.
- **Many transitions** — each point where one color sits on a different color represents future work that must be undone.

---

## Move Pruning

These moves are legal but produce no progress. A solver should skip them.

**Empty to empty.** Moving nothing between two empty tubes changes nothing.

**Complete tube as source.** Pouring from a complete tube disrupts solved work.

**Redundant empty tube destinations.** When multiple empty tubes exist, pouring into any one produces an equivalent state. Only explore one — the others are duplicates.

**Immediate reversal.** Pouring A→B then immediately B→A returns to the previous state and contributes nothing.

---

## Progress Indicators

**Consolidation count.** The number of colors fully resolved into their own complete tube. Each consolidation permanently reduces the problem size.

**Fragmentation score.** For each color, count how many distinct tubes it appears in. A color spread across more tubes requires more moves. Progress means this number decreasing.

**Transition count.** Within each tube, count the points where one color sits on top of a different color. Fewer transitions means closer to the goal.

**Available space.** A board that retains empty or partially empty tubes retains flexibility. Filling tubes without resolving colors consumes space without making progress.

---

## Invariants

These hold across every valid state and can be relied on unconditionally:

- The total count of each color's layers never changes. Colors are moved, not created or destroyed.
- Total tube capacity never changes. Space is conserved.
- A completed tube never needs to be touched again.
- Every valid solution must place each color entirely within one tube.

---

## Limitations and Edge Cases

**Zero empty tubes.** Most puzzles are unsolvable with no empty tubes. The only exception is a configuration where colors are already partially consolidated and no circular dependencies exist.

**One empty tube.** Solvable in some cases, but the solver's search space grows significantly — there is no slack for mistakes.

**Unsolvable puzzles.** If the solver returns no solution, the puzzle is either unsolvable or the input is invalid (e.g., unequal color counts). Verify that each color appears exactly `capacity` times across all tubes.

**Identical colors.** If two distinct colors are represented by the same label in the input, the solver treats them as one color and will produce incorrect results.

---

## Summary: What Any Solver Must Implement

Regardless of algorithm, a correct solver requires:

- State representation as an ordered collection of tubes, supporting equality comparison and canonical ordering for deduplication.
- Move generation that enforces all four validity rules and correctly computes the multi-layer pour quantity.
- Goal detection that checks each tube for the uniform-and-full or empty condition.
- Visited state tracking using canonical form to prevent cycles.
- Move pruning to eliminate empty-to-empty, complete-source, redundant empty-destination, and reversal moves.
- Deadlock detection for circular dependencies and space exhaustion.
- Progress measurement using consolidation count, fragmentation score, and transition count.

These are the foundations. The algorithm layered on top is a separate decision — but no algorithm works correctly or efficiently without these in place.