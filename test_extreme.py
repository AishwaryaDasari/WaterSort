from moves import get_top_run, apply_move
from solver import solve_greedy
from entropy import entropy_score

# Test 1: 12 colors (extreme)
TEST_12_COLORS = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    ('P', 'O', 'W', 'K'),
    ('O', 'P', 'K', 'W'),
    ('W', 'K', 'O', 'P'),
    ('K', 'W', 'P', 'O'),
    ('A', 'C', 'D', 'E'),
    ('C', 'A', 'E', 'D'),
    ('D', 'E', 'A', 'C'),
    ('E', 'D', 'C', 'A'),
    (),
)

# Test 2: Maximum fragmentation (every layer different)
TEST_MAX_FRAG = (
    ('R', 'G', 'B', 'Y'),
    ('Y', 'R', 'G', 'B'),
    ('B', 'Y', 'R', 'G'),
    ('G', 'B', 'Y', 'R'),
    (),
)

# Test 3: Deep nesting (colors buried deep)
TEST_DEEP_NEST = (
    ('R', 'B', 'G', 'Y'),
    ('B', 'G', 'Y', 'R'),
    ('G', 'Y', 'R', 'B'),
    ('Y', 'R', 'B', 'G'),
    (),
)

# Test 4: 15 colors (extreme scale)
TEST_15_COLORS = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    ('P', 'O', 'W', 'K'),
    ('O', 'P', 'K', 'W'),
    ('W', 'K', 'O', 'P'),
    ('K', 'W', 'P', 'O'),
    ('A', 'C', 'D', 'E'),
    ('C', 'A', 'E', 'D'),
    ('D', 'E', 'A', 'C'),
    ('E', 'D', 'C', 'A'),
    ('F', 'H', 'J', 'L'),
    ('H', 'F', 'L', 'J'),
    ('J', 'L', 'F', 'H'),
    (),
)

# Test 5: Capacity 5 (larger tubes)
TEST_CAPACITY_5 = (
    ('R', 'B', 'G', 'Y', 'P'),
    ('G', 'R', 'Y', 'B', 'P'),
    ('Y', 'G', 'B', 'R', 'P'),
    ('B', 'Y', 'R', 'G', 'P'),
    ('P', 'P', 'P', 'P', 'P'),
    (),
)

def test_puzzle(name, puzzle, capacity, max_moves=1000):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    num_colors = len(set(c for tube in puzzle for c in tube))
    print(f"Colors: {num_colors}")
    print(f"Tubes: {len(puzzle)}")
    print(f"Capacity: {capacity}")
    print(f"Initial entropy: {entropy_score(puzzle, capacity):.4f}")
    
    import time
    start = time.time()
    path = solve_greedy(puzzle, capacity, max_moves=max_moves)
    elapsed = time.time() - start
    
    if path is None:
        print(f"FAILED: No solution found (timeout or stuck)")
        print(f"Time: {elapsed:.2f}s")
        return False
    
    # Verify solution
    state = puzzle
    for i, j in path:
        state = apply_move(state, i, j, capacity)
    
    final_entropy = entropy_score(state, capacity)
    print(f"Solution found: {len(path)} moves")
    print(f"Final entropy: {final_entropy:.4f}")
    print(f"Time: {elapsed:.2f}s")
    
    # Check if actually solved
    all_complete = all(
        len(tube) == 0 or (len(tube) == capacity and len(set(tube)) == 1)
        for tube in state
    )
    
    if all_complete:
        print("STATUS: SOLVED")
        return True
    else:
        print("STATUS: INCOMPLETE")
        return False

if __name__ == "__main__":
    results = []
    
    results.append(("Max fragmentation", test_puzzle("Maximum Fragmentation", TEST_MAX_FRAG, 4)))
    results.append(("Deep nesting", test_puzzle("Deep Nesting", TEST_DEEP_NEST, 4)))
    results.append(("12 colors", test_puzzle("12 Colors - Extreme", TEST_12_COLORS, 4)))
    results.append(("Capacity 5", test_puzzle("Capacity 5 - Larger Tubes", TEST_CAPACITY_5, 5)))
    results.append(("15 colors", test_puzzle("15 Colors - Extreme Scale", TEST_15_COLORS, 4, max_moves=2000)))
    
    print(f"\n{'='*60}")
    print("EXTREME TESTS SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{name:30s} {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} passed")
