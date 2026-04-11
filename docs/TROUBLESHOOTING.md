# Troubleshooting Guide

## Common Issues and Solutions

### "Solver returns None"

**Symptom:** `solve()` returns `None` instead of a path.

**Possible Causes:**

1. **Unsolvable puzzle** - The puzzle has no valid solution
   - Check: Does each color appear exactly `capacity` times total?
   - Check: Is there at least one empty tube?
   - Check: Are there circular dependencies with no empty tubes?

2. **Invalid initial state**
   - Check: Are all tubes within capacity limits?
   - Check: Are color labels consistent (no typos)?

3. **Bug in move generation**
   - Debug: Run `get_valid_moves(initial_state, capacity)` and print result
   - If empty, check `is_valid_move()` logic

4. **Bug in goal detection**
   - Debug: Create a known goal state manually and verify `is_goal()` returns `True`

**Example of unsolvable puzzle:**
```python
# No empty tube, circular dependency
state = (('R', 'B'), ('B', 'R'))  # capacity=2
# R needs to go on R, but B is blocking in both tubes
```

---

### "Solution is longer than expected"

**Symptom:** Solver returns a valid solution but with more moves than optimal.

**Possible Causes:**

1. **Using DFS or Greedy** - These don't guarantee optimal solutions
   - Fix: Use BFS, IDDFS, or A* for guaranteed optimality

2. **Heuristic is not admissible** (A* only)
   - Debug: Add `print(heuristic(goal_state))` - must return 0
   - Check: Does `fragmentation_score(goal_state)` return 0?
   - Check: Does `transition_score(goal_state)` return 0?

3. **Canonical form not working**
   - Debug: Check if equivalent states have same canonical form
   - Test: `canonical((('R','B'), ('G',))) == canonical((('G',), ('R','B')))`

**Diagnostic steps:**
```python
# Test heuristic on goal state
goal = (('R','R','R','R'), ('G','G','G','G'), ())
assert heuristic(goal) == 0, f"Heuristic should be 0, got {heuristic(goal)}"

# Test fragmentation on solved state
assert fragmentation_score(goal) == 0

# Test transitions on uniform tubes
assert transition_score((('R','R','R'),)) == 0
```

---

### "Solver runs forever / very slow"

**Symptom:** Solver doesn't finish within reasonable time.

**Possible Causes:**

1. **Visited set not working** - Exploring duplicate states infinitely
   - Debug: Add counter in solve loop: `if len(visited) % 1000 == 0: print(len(visited))`
   - If counter grows without bound, canonical form has a bug

2. **Puzzle is too large** - Exponential growth with color count
   - BFS/IDDFS struggle with 6+ colors
   - A* can handle up to ~10 colors depending on fragmentation

3. **No pruning** - Exploring redundant moves
   - Check: Is `get_valid_moves()` filtering empty-to-empty moves?
   - Check: Is it skipping complete tubes as sources?

4. **Heuristic is too loose** (A* only)
   - If h(state) is always 0, A* degrades to BFS
   - Debug: Print h values during search

**Performance expectations:**
```
4 colors, 5 tubes:  A* ~14 nodes,    BFS ~66 nodes
6 colors, 7 tubes:  A* ~200 nodes,   BFS ~15,000 nodes
10 colors, 11 tubes: A* ~10,000 nodes, BFS impractical
```

---

### "TypeError: '<' not supported between instances of 'tuple'"

**Symptom:** Crash in A* heap operations.

**Cause:** Missing counter tiebreaker in heap entries.

**Fix:** Ensure heap entries include a unique counter:
```python
counter = 0
heapq.heappush(open_set, (f, g, counter, state, path))
counter += 1  # Increment for each push
```

The counter prevents Python from comparing state tuples when f and g values are equal.

---

### "Move count in output doesn't match path length"

**Symptom:** Final output says "Solved in 13 moves" but only 10 moves were printed.

**Cause:** Pour count computed after `apply_move()` instead of before.

**Fix:** Compute pour details BEFORE applying the move:
```python
for move_number, (i, j) in enumerate(path, start=1):
    # Compute BEFORE apply_move
    top_color, run_len = get_top_run(state[i])
    available = TUBE_CAPACITY - len(state[j])
    pour_count = min(run_len, available)
    
    # Now apply the move
    state = apply_move(state, i, j, TUBE_CAPACITY)
    
    # Print with correct pour_count
    print_move(move_number, i, j, pour_count, top_color, state)
```

---

### "State mutation bug"

**Symptom:** Visited states are corrupted, solver produces invalid results.

**Cause:** `apply_move()` modifies existing state instead of creating a copy.

**Fix:** Always create new tuples:
```python
def apply_move(state, i, j, capacity):
    tubes = [list(t) for t in state]  # Create copies
    # ... modify tubes ...
    return tuple(tuple(t) for t in tubes)  # Return new state
```

Never do: `state[i].pop()` - tuples are immutable, this will crash.

---

### "DFS returns suboptimal solution"

**Symptom:** DFS finds a solution but it's longer than BFS/A*.

**Cause:** DFS explores depth-first and returns the first solution found, which may not be optimal.

**This is expected behavior.** DFS does not guarantee optimal solutions.

**Solutions:**
- Use BFS, IDDFS, or A* if optimality is required
- Use DFS only when solution length doesn't matter or memory is severely constrained

**Example where DFS fails:**
```python
# Simple puzzle: T0:[R,B]  T1:[B,R]  T2:[]  (capacity=2)
# Optimal: 4 moves
# DFS might find: 6 moves (if it explores a detour branch first)
```

---

### "Greedy gets stuck / returns no solution"

**Symptom:** Greedy search reaches a state with no valid moves or returns None.

**Cause:** Greedy always picks the locally best move without backtracking. Can reach dead ends.

**This is expected behavior.** Greedy does not guarantee finding a solution.

**Example where Greedy fails:**
```python
# T0:[R,G,B]  T1:[B,R,G]  T2:[G,B,R]  T3:[]  (capacity=3)
# Greedy might pour T0→T3, then get stuck with no good moves
# A* would explore alternative first moves
```

**Solutions:**
- Use A* for guaranteed optimal solutions
- Use Greedy only for fast approximate solutions where failure is acceptable

---

## Diagnostic Checklist

When debugging, check these in order:

1. **Input validation**
   - [ ] Each color appears exactly `capacity` times total
   - [ ] At least one empty tube exists (for most puzzles)
   - [ ] No tube exceeds capacity
   - [ ] Color labels are consistent

2. **State representation**
   - [ ] States are tuples of tuples (immutable)
   - [ ] `canonical()` sorts tubes consistently
   - [ ] `is_goal()` returns True for known goal states

3. **Move generation**
   - [ ] `get_valid_moves()` returns non-empty list for initial state
   - [ ] `apply_move()` creates new state, doesn't modify existing
   - [ ] Pour quantity computed correctly: min(run_length, available_space)

4. **Heuristic (A* only)**
   - [ ] `heuristic(goal_state)` returns 0
   - [ ] `fragmentation_score()` counts tubes per color correctly
   - [ ] `transition_score()` counts color changes correctly

5. **Search algorithm**
   - [ ] Visited set uses canonical form
   - [ ] Heap entries include counter tiebreaker (A*)
   - [ ] Goal check happens at correct point in loop

---

## Performance Debugging

### Add instrumentation to solver:

```python
def solve(initial_state, capacity):
    nodes_explored = 0
    max_heap_size = 0
    
    # ... existing code ...
    
    while open_set:
        nodes_explored += 1
        max_heap_size = max(max_heap_size, len(open_set))
        
        if nodes_explored % 1000 == 0:
            print(f"Explored: {nodes_explored}, Heap: {len(open_set)}, Visited: {len(visited)}")
        
        # ... rest of solve logic ...
    
    print(f"Total nodes explored: {nodes_explored}")
    print(f"Max heap size: {max_heap_size}")
    print(f"Visited states: {len(visited)}")
```

### Expected output for 4-color baseline:
```
Total nodes explored: 14
Max heap size: ~14
Visited states: 14
```

If numbers are much higher, there's a bug in pruning or canonical form.

---

## Testing Strategy

### Unit tests for each component:

```python
# test_state.py
def test_canonical_equivalence():
    s1 = (('R', 'B'), ('G', 'Y'))
    s2 = (('G', 'Y'), ('R', 'B'))
    assert canonical(s1) == canonical(s2)

def test_goal_detection():
    goal = (('R', 'R'), ('B', 'B'), ())
    assert is_goal(goal, capacity=2) == True
    
    partial = (('R',), ('B', 'B'), ())
    assert is_goal(partial, capacity=2) == False

# test_moves.py
def test_multi_layer_pour():
    state = (('R', 'B', 'G', 'G'), ('G',), ())
    result = apply_move(state, 0, 1, capacity=4)
    assert result[0] == ('R', 'B')  # 2×G removed
    assert result[1] == ('G', 'G', 'G')  # 2×G added

# test_heuristic.py
def test_heuristic_zero_on_goal():
    goal = (('R', 'R', 'R'), ('B', 'B', 'B'), ())
    assert heuristic(goal) == 0
```

Run with: `uv run pytest -v`

---

## When to Ask for Help

If you've checked all of the above and still have issues:

1. Create a minimal reproducible example
2. Include the exact puzzle configuration
3. Show the output or error message
4. Mention which algorithm you're using
5. Include any diagnostic output from instrumentation

Example bug report:
```
Algorithm: A*
Puzzle: 4 colors, 5 tubes, capacity 4
Initial state: (('R','B','G','Y'), ('G','R','Y','B'), ...)
Issue: Returns None (no solution)
Diagnostic: get_valid_moves() returns 8 moves from initial state
Diagnostic: heuristic(initial) = 24
Expected: Should find 13-move solution
```
