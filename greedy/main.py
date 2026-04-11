from moves import get_top_run, apply_move
from solver import solve_greedy
from printer import print_initial, print_move, print_solution
from entropy import entropy_score

TUBE_CAPACITY = 4

INITIAL_STATE = (
    ('R', 'B', 'G', 'Y'),
    ('G', 'R', 'Y', 'B'),
    ('Y', 'G', 'B', 'R'),
    ('B', 'Y', 'R', 'G'),
    (),
)

def main():
    print_initial(INITIAL_STATE)
    print(f"Initial entropy: {entropy_score(INITIAL_STATE, TUBE_CAPACITY):.4f}\n")
    
    path = solve_greedy(INITIAL_STATE, TUBE_CAPACITY)
    
    if path is None:
        print("No solution found.")
        return
    
    state = INITIAL_STATE
    for move_number, (i, j) in enumerate(path, start=1):
        top_color, run_len = get_top_run(state[i])
        available = TUBE_CAPACITY - len(state[j])
        pour_count = min(run_len, available)
        state = apply_move(state, i, j, TUBE_CAPACITY)
        e = entropy_score(state, TUBE_CAPACITY)
        print_move(move_number, i, j, pour_count, top_color, state)
        print(f"  Entropy: {e:.4f}\n")
    
    print_solution(len(path))

if __name__ == "__main__":
    main()
