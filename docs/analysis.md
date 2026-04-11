# Water Sort: A High-Level Analysis

---

## What Is Water Sort?

Water Sort is a logic-based puzzle game built around one constraint: colored water can only be poured onto water of the same color, and only if there is space to receive it. You are given a set of tubes — each holding four units — filled with mixed layers of color. The objective is to reach a state where every tube contains exactly one color, solid from bottom to top.

The game has no timer, no randomness, and no hidden information. Every tube, every layer, every color is visible to you at all times. This makes it a game of **pure logic**, not reflexes or luck. If you fail, the board did not beat you — your reasoning did.

---

## The Structure of the Problem

Before making a single move, it helps to understand what kind of problem you are actually solving.

Each level is essentially a **sorting problem with constrained operations**. Think of it like this: you have data (colors) stored in stacks (tubes), and you can only move data under specific conditions. This is structurally similar to problems in computer science — specifically the Tower of Hanoi or stack-sorting problems — where the challenge is not *what* the final state looks like, but *what sequence of moves* gets you there within the rules.

The key insight is that **the end state is always known**. You know exactly how many colors exist, and you know each color must end up alone in a tube. The entire puzzle is about working out the path from disorder to that known order.

---

## The Logical Principles

### 1. Think in Terms of Layers, Not Tubes

Most beginners look at tubes as units. Analytical players look at **layers** as units. Each layer has a color, a position within its tube, and a set of conditions under which it can move. Before touching anything, mentally map out which layers are "accessible" (on top) and which are buried. A buried layer cannot move until everything above it is cleared. This immediately tells you which moves are even possible at any given moment.

### 2. Understand Dependency Chains

Every buried layer creates a dependency. To move color A, you must first move color B sitting on top of it. But to move color B, you may need to move color C elsewhere first. These form **chains of dependencies** that can be several moves deep.

Tracing these chains before acting is what separates analytical play from random play. Ask: *what needs to happen before this layer becomes accessible?* Follow that chain to its root, and you have a natural sequence of moves to execute.

### 3. The Role of Empty Tubes

Empty tubes are not just "extra space" — they are **the mechanism by which deadlocks are broken**. When a dependency chain has no natural resolution (color B has nowhere to go while you're trying to uncover color A), an empty tube acts as a buffer: a temporary home that makes the chain solvable.

The critical analytical habit is to **never fill an empty tube without a plan to empty it again**. Treating empty tubes as permanent storage is one of the fastest ways to run out of options.

### 4. Deadlock Recognition

A deadlock is a state where no productive move exists. In Water Sort, deadlocks typically form in one of two ways:

- **Circular dependency**: Color A is trapped under Color B, Color B is trapped under Color A, and there is no empty tube to break the cycle.
- **Space exhaustion**: Every tube is either full or topped with a color that has no valid destination.

The analytical skill here is recognizing a *developing* deadlock — not after it has fully formed, but two or three moves before it becomes unavoidable. This requires thinking ahead rather than reacting to the current state.

### 5. Color Consolidation as a Priority

Every time you fully consolidate a color into a single tube, you effectively **reduce the complexity of the puzzle**. A completed tube is frozen — it no longer participates in the problem. This shrinks the active search space and gives you cleaner visibility into what remains.

Strategically, this means you should look for colors that are *close* to consolidation — where most of their layers are already together or accessible — and prioritize completing those first. Early consolidation creates momentum and frees resources for harder colors.

### 6. Working Backwards From the Goal

Since the end state is always known, you can reason in reverse. Ask: *for the final arrangement to exist, what must the second-to-last state have looked like?* This reverse reasoning is particularly useful when you are stuck, because it reframes the question from "what can I do?" to "what must have happened just before the solution?" — a much more constrained and answerable question.

---

## The Mental Model to Carry Into Every Level

Before making any move, build a mental map with three things:

1. **Accessibility** — which layers can actually move right now?
2. **Destination** — where does each accessible layer ultimately belong?
3. **Consequences** — what does this move open up, and what does it close off?

A move that is *legal* and a move that is *good* are not the same thing. Legal means the rules allow it. Good means it moves the board closer to resolution without creating a problem that costs more moves to undo than the move itself was worth.

The game is essentially asking you, at every step, to evaluate tradeoffs between immediate gain and future flexibility. That is the analytical core of Water Sort — and once you see it that way, the puzzles become a structured thinking exercise rather than a guessing game.
