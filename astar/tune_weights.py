from moves import apply_move
from solver_beam import solve_beam
from entropy import entropy_score
import entropy as ent

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

def test_weights(alpha, beta, gamma):
    # Temporarily modify entropy function
    original_func = ent.entropy_score
    
    def custom_entropy(state, capacity, a=alpha, b=beta, g=gamma):
        num_tubes = len(state)
        h_norm = ent.normalized_shannon_entropy(state, num_tubes)
        v_score = ent.vertical_entropy(state, capacity)
        empty_r = ent.empty_ratio(state, num_tubes)
        E = a * h_norm + b * v_score - g * empty_r
        return max(0.0, E)
    
    ent.entropy_score = custom_entropy
    
    import time
    start = time.time()
    path = solve_beam(PUZZLE_12C_15T, TUBE_CAPACITY, beam_width=20, max_depth=150)
    elapsed = time.time() - start
    
    ent.entropy_score = original_func
    
    if path:
        state = PUZZLE_12C_15T
        for i, j in path:
            state = apply_move(state, i, j, TUBE_CAPACITY)
        solved = all(len(t) == 0 or (len(t) == TUBE_CAPACITY and len(set(t)) == 1) for t in state)
        return (True, len(path), elapsed) if solved else (False, len(path), elapsed)
    return (False, 0, elapsed)

if __name__ == "__main__":
    print("Testing different weight combinations:\n")
    
    configs = [
        (0.6, 0.4, 0.1, "Default"),
        (0.7, 0.3, 0.1, "More Shannon"),
        (0.5, 0.5, 0.1, "Equal Shannon/Vertical"),
        (0.8, 0.2, 0.1, "Heavy Shannon"),
        (0.6, 0.4, 0.2, "More empty bonus"),
        (0.4, 0.6, 0.1, "More Vertical"),
    ]
    
    for alpha, beta, gamma, name in configs:
        print(f"{name:25s} (α={alpha}, β={beta}, γ={gamma}): ", end="", flush=True)
        solved, moves, time = test_weights(alpha, beta, gamma)
        if solved:
            print(f"SOLVED in {moves} moves ({time:.2f}s)")
        else:
            print(f"FAILED ({time:.2f}s)")
