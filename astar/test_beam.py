from moves import apply_move
from solver_beam import solve_beam
from printer import print_initial, print_solution
from entropy import entropy_score

TUBE_CAPACITY = 4

PUZZLE_12C_15T = (
    ('A', 'B', 'C', 'D'),
    ('E', 'F', 'G', 'H'),
    ('I', 'J', 'K', 'L'),
    ('B', 'C', 'D', 'A'),
    ('F', 'G', 'H', 'E'),
    ('J', 'K', 'L', 'I'),
    ('C', 'D', 'A', 'B'),
    ('G', 'H', 'E', 'F'),
    ('K', 'L', 'I', 'J'),
    ('D', 'A', 'B', 'C'),
    ('H', 'E', 'F', 'G'),
    ('L', 'I', 'J', 'K'),
    ('A', 'E', 'I', 'B'),
    (),
    (),
)

def main():
    print("="*60)
    print("12 Colors, 15 Tubes - Beam Search")
    print("="*60)
    print_initial(PUZZLE_12C_15T)
    
    num_colors = len(set(c for tube in PUZZLE_12C_15T for c in tube))
    print(f"Colors: {num_colors}, Tubes: {len(PUZZLE_12C_15T)}")
    print(f"Initial entropy: {entropy_score(PUZZLE_12C_15T, TUBE_CAPACITY):.4f}\n")
    
    import time
    start = time.time()
    path = solve_beam(PUZZLE_12C_15T, TUBE_CAPACITY, beam_width=20, max_depth=150)
    elapsed = time.time() - start
    
    if path is None:
        print(f"\nFAILED: No solution found")
        print(f"Time: {elapsed:.2f}s")
        return
    
    print(f"\nSolution found in {elapsed:.2f}s!")
    print(f"Moves: {len(path)}")
    
    # Verify
    state = PUZZLE_12C_15T
    for i, j in path:
        state = apply_move(state, i, j, TUBE_CAPACITY)
    
    final_entropy = entropy_score(state, TUBE_CAPACITY)
    all_complete = all(
        len(tube) == 0 or (len(tube) == TUBE_CAPACITY and len(set(tube)) == 1)
        for tube in state
    )
    
    print(f"Final entropy: {final_entropy:.4f}")
    print(f"Status: {'SOLVED' if all_complete else 'INCOMPLETE'}")
    print_solution(len(path))

if __name__ == "__main__":
    main()
