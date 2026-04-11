from state import is_complete

def get_top_run(tube):
    if not tube:
        return (None, 0)
    top_color = tube[-1]
    count = sum(1 for layer in reversed(tube) if layer == top_color)
    return (top_color, count)

def is_valid_move(state, i, j, capacity):
    src, dst = state[i], state[j]
    if not src or is_complete(src, capacity) or len(dst) == capacity:
        return False
    if dst and dst[-1] != src[-1]:
        return False
    return True

def apply_move(state, i, j, capacity):
    tubes = [list(t) for t in state]
    top_color, run_len = get_top_run(tubes[i])
    pour_count = min(run_len, capacity - len(tubes[j]))
    for _ in range(pour_count):
        tubes[i].pop()
    tubes[j].extend([top_color] * pour_count)
    return tuple(tuple(t) for t in tubes)

def get_valid_moves(state, capacity):
    moves = []
    n = len(state)
    first_empty = next((k for k in range(n) if not state[k]), None)
    
    for i in range(n):
        for j in range(n):
            if i == j or not is_valid_move(state, i, j, capacity):
                continue
            if not state[j] and j != first_empty:
                continue
            src_top, run_len = get_top_run(state[i])
            if not state[j] and run_len == len(state[i]):
                continue
            moves.append((i, j))
    
    return moves
