# Water Sort: Analysis, Rules, and Logic

---

## What Is Water Sort?

Water Sort is a logic-based puzzle game. You are given a set of tubes, each filled with mixed layers of color. The goal is to sort them so every tube contains exactly one color from bottom to top.

The number of tubes, the capacity of each tube, and the number of colors all vary by level — there is no fixed format. What stays constant is the rule system.

The game has no timer, no randomness, and no hidden information. Every tube and every layer is visible at all times. It is a game of pure logic — if you fail, your reasoning failed, not the board.

---

## The Game Model

Each tube holds an ordered sequence of color layers. Only the topmost layer is accessible at any time. This makes each tube a stack — you can only interact with what is on top.

A game state is a complete snapshot of all tubes and their contents at a given moment. Every move takes one state and produces a new one.

---

## Rules of a Move

A move means pouring from a source tube into a destination tube. All of the following conditions must hold. If any one fails, the move is illegal.

**Rule 1 — Source must not be empty.** There is nothing to pour from an empty tube.

**Rule 2 — Source must not be already complete.** A tube is complete when it holds a single uniform color at full capacity. Pouring from it undoes solved work and serves no purpose.

**Rule 3 — Destination must not be full.** The destination must have at least one unit of free space.

**Rule 4 — Colors must match, or destination must be empty.** The top color of the source must equal the top color of the destination. The only exception is an empty destination, which accepts any color.

---

## The Pour Quantity Rule

A pour is not always a single layer. All consecutive matching layers from the top of the source pour together as one action, subject to available space in the destination.

- The number of same-color layers at the top of the source is the **run length**.
- The number of free units in the destination is the **available space**.
- Layers transferred = minimum of run length and available space.

This is the most commonly misunderstood mechanic. A solver that assumes one-layer-at-a-time transfers will produce incorrect move sequences.

---

## Goal Condition

The puzzle is solved when every tube satisfies one of these two conditions:

- The tube is completely empty, or
- The tube is filled entirely with a single color — no gaps, no mixed layers.

A partially filled tube with matching layers does not count as solved unless it is at full capacity.

---

## State Identity and Canonical Form

Two states are identical when every tube contains the exact same layers in the exact same order. Layer order within a tube matters because it determines which moves are possible.

The physical position of tubes on the board carries no meaning. A solver exploits this by sorting the list of tubes into a canonical order before comparing or storing states. Two board configurations with the same tubes in different positions are treated as one state. This significantly reduces the number of distinct states any solver needs to track.

---

## Logical Principles for Solving

### Think in Layers, Not Tubes

A buried layer cannot move until everything above it is cleared. Before making any move, identify which layers are accessible (on top) and which are not. This tells you immediately what moves are possible.

### Trace Dependency Chains

Every buried layer creates a dependency. To reach color A, you may need to move color B first. To move color B, you may need to move color C. These chains can run several moves deep. Tracing a chain to its root before acting gives you a natural sequence of moves to execute.

### Preserve Empty Tubes

Empty tubes are not spare space — they are the mechanism by which deadlocks are broken. When a dependency chain has no natural resolution, an empty tube provides a temporary holding place that makes the chain solvable. Never fill an empty tube without a clear plan to empty it again.

### Prioritise Color Consolidation

Every time a color is fully gathered into one complete tube, the problem shrinks. A completed tube is permanently removed from the active puzzle. Look for colors that are close to consolidation and resolve those first — early completions create space and momentum for harder colors.

### Work Backwards From the Goal

The end state is always known. When stuck, ask what the board must have looked like one move before the solution. Reverse reasoning turns "what can I do?" into "what must have happened?" — a much more constrained and solvable question.

---

## Deadlock Conditions

A deadlock is a state from which no sequence of moves reaches the goal.

**Circular dependency.** Color A is trapped under color B in one tube, and color B is trapped under color A in another tube, with no empty tube available to break the cycle. Neither can move.

**Space exhaustion.** Every tube is either full or topped with a color that has no valid destination. No move is possible anywhere on the board.

A solver should detect developing deadlocks two or three moves before they fully form, and prune those branches early.

---

## Move Pruning

These moves are legal under the rules but produce no progress. A solver should skip them entirely.

**Empty to empty.** Pouring from one empty tube into another changes nothing.

**Complete tube as source.** Pouring from an already-complete tube disrupts solved work.

**Redundant empty tube destinations.** When multiple empty tubes exist, pouring a color into any one of them produces an equivalent state. Only one needs to be explored — the rest are duplicates.

**Immediate reversal.** Pouring from tube A to tube B, then immediately back from tube B to tube A, returns to the previous state. This contributes nothing.

---

## Progress Indicators

These measures tell a solver whether the board is genuinely moving toward the goal.

**Consolidation count.** The number of colors fully resolved into their own complete tube. Each consolidation permanently reduces the problem size.

**Fragmentation score.** For each color, count how many distinct tubes it appears in. A color spread across more tubes requires more moves to consolidate. Progress means this number decreasing.

**Transition count.** Within each tube, count the points where one color sits on top of a different color. Each such point represents future work that must be undone. Fewer transitions means closer to the goal.

**Available space.** A board that retains empty or partially empty tubes retains flexibility. Filling tubes without resolving colors consumes space without making progress.

---

## Invariants

These properties hold across every state in a valid game and can be relied on unconditionally.

- The total count of each color's layers never changes. Colors are moved, not created or destroyed.
- Total tube capacity across the board never changes. Space is conserved.
- A completed tube never needs to be touched again.
- Every valid solution must eventually place each color entirely within one tube.

---

## Summary: What Any Solver Must Implement

Regardless of which algorithm is used, a correct and efficient solver requires all of the following:

- State representation as an ordered collection of tubes, supporting equality comparison and canonical ordering for deduplication.
- Move generation that enforces all four validity rules and correctly computes the multi-layer pour quantity.
- Goal detection that checks each tube for the uniform-and-full or empty condition.
- Visited state tracking using canonical form to prevent cycles.
- Move pruning to eliminate empty-to-empty, complete-source, redundant empty-destination, and reversal moves.
- Deadlock detection for circular dependencies and space exhaustion.
- Progress measurement using consolidation count, fragmentation score, and transition count.

These are the foundations. The algorithm layered on top is a separate decision — but no algorithm works correctly or efficiently without these in place.