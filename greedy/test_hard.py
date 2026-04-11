from moves import get_top_run, apply_move
from solver import solve_greedy
from entropy import entropy_score

# Test 1: 6 colors, 7 tubes (medium difficulty)
TEST_6_COLORS = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    ('P', 'O', 'P', 'O'),
    ('O', 'P', 'O', 'P'),
    (),
)

# Test 2: 8 colors, 9 tubes (hard)
TEST_8_COLORS = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    ('P', 'O', 'W', 'K'),
    ('O', 'P', 'K', 'W'),
    ('W', 'K', 'O', 'P'),
    ('K', 'W', 'P', 'O'),
    (),
)

# Test 3: 5 colors with high fragmentation
TEST_HIGH_FRAG = (
    ('R', 'G', 'B', 'Y'),
    ('B', 'R', 'Y', 'G'),
    ('Y', 'B', 'G', 'R'),
    ('G', 'Y', 'R', 'B'),
    ('P', 'P', 'P', 'P'),
    (),
)

# Test 4: 4 colors, only 1 empty tube (constrained)
TEST_ONE_EMPTY = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    (),
)

# Test 5: 10 colors, 11 tubes (very hard)
TEST_10_COLORS = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    ('P', 'O', 'W', 'K'),
    ('O', 'P', 'K', 'W'),
    ('W', 'K', 'O', 'P'),
    ('K', 'W', 'P', 'O'),
    ('A', 'C', 'A', 'C'),
    ('C', 'A', 'C', 'A'),
    (),
)

def test_puzzle(name, puzzle, capacity):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(f"Colors: {len(set(c for tube in puzzle for c in tube))}")
    print(f"Tubes: {len(puzzle)}")
    print(f"Capacity: {capacity}")
    print(f"Initial entropy: {entropy_score(puzzle, capacity):.4f}")
    
    path = solve_greedy(puzzle, capacity, max_moves=500)
    
    if path is None:
        print("FAILED: No solution found")
        return False
    
    # Verify solution
    state = puzzle
    for i, j in path:
        state = apply_move(state, i, j, capacity)
    
    final_entropy = entropy_score(state, capacity)
    print(f"Solution found: {len(path)} moves")
    print(f"Final entropy: {final_entropy:.4f}")
    
    # Check if actually solved
    all_complete = all(
        len(tube) == 0 or (len(tube) == capacity and len(set(tube)) == 1)
        for tube in state
    )
    
    if all_complete:
        print("STATUS: SOLVED")
        return True
    else:
        print("STATUS: INCOMPLETE (not fully solved)")
        return False

if __name__ == "__main__":
    results = []
    
    results.append(("6 colors (medium)", test_puzzle("6 Colors - Medium", TEST_6_COLORS, 4)))
    results.append(("High fragmentation", test_puzzle("5 Colors - High Fragmentation", TEST_HIGH_FRAG, 4)))
    results.append(("1 empty tube", test_puzzle("4 Colors - Only 1 Empty", TEST_ONE_EMPTY, 4)))
    results.append(("8 colors (hard)", test_puzzle("8 Colors - Hard", TEST_8_COLORS, 4)))
    results.append(("10 colors (very hard)", test_puzzle("10 Colors - Very Hard", TEST_10_COLORS, 4)))
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{name:30s} {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} passed")
