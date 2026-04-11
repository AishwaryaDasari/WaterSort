from moves import get_top_run, apply_move
from solver import solve_greedy
from printer import print_initial, print_move, print_solution
from entropy import entropy_score

TUBE_CAPACITY = 4

# 12 colors, 15 tubes (2 empty)
PUZZLE_12C_15T = (
    ('A', 'B', 'C', 'D'),  # T0
    ('E', 'F', 'G', 'H'),  # T1
    ('I', 'J', 'K', 'L'),  # T2
    ('B', 'C', 'D', 'A'),  # T3
    ('F', 'G', 'H', 'E'),  # T4
    ('J', 'K', 'L', 'I'),  # T5
    ('C', 'D', 'A', 'B'),  # T6
    ('G', 'H', 'E', 'F'),  # T7
    ('K', 'L', 'I', 'J'),  # T8
    ('D', 'A', 'B', 'C'),  # T9
    ('H', 'E', 'F', 'G'),  # T10
    ('L', 'I', 'J', 'K'),  # T11
    ('A', 'E', 'I', 'B'),  # T12
    (),                     # T13 (empty)
    (),                     # T14 (empty)
)

def main():
    print("="*60)
    print("12 Colors, 15 Tubes Puzzle")
    print("="*60)
    print_initial(PUZZLE_12C_15T)
    
    num_colors = len(set(c for tube in PUZZLE_12C_15T for c in tube))
    print(f"Colors: {num_colors}")
    print(f"Tubes: {len(PUZZLE_12C_15T)}")
    print(f"Empty tubes: {sum(1 for t in PUZZLE_12C_15T if len(t) == 0)}")
    print(f"Initial entropy: {entropy_score(PUZZLE_12C_15T, TUBE_CAPACITY):.4f}\n")
    
    import time
    start = time.time()
    path = solve_greedy(PUZZLE_12C_15T, TUBE_CAPACITY, max_moves=5000)
    elapsed = time.time() - start
    
    if path is None:
        print("FAILED: No solution found")
        print(f"Time: {elapsed:.2f}s")
        return
    
    print(f"Solution found in {elapsed:.2f}s!\n")
    
    state = PUZZLE_12C_15T
    for move_number, (i, j) in enumerate(path, start=1):
        top_color, run_len = get_top_run(state[i])
        available = TUBE_CAPACITY - len(state[j])
        pour_count = min(run_len, available)
        state = apply_move(state, i, j, TUBE_CAPACITY)
        e = entropy_score(state, TUBE_CAPACITY)
        print_move(move_number, i, j, pour_count, top_color, state)
        print(f"  Entropy: {e:.4f}\n")
    
    print_solution(len(path))
    
    # Verify solution
    all_complete = all(
        len(tube) == 0 or (len(tube) == TUBE_CAPACITY and len(set(tube)) == 1)
        for tube in state
    )
    
    if all_complete:
        print("\nVERIFIED: Puzzle completely solved!")
    else:
        print("\nWARNING: Solution incomplete")

if __name__ == "__main__":
    main()
