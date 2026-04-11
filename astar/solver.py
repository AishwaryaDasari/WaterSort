import heapq
from state import canonical, is_goal
from moves import get_valid_moves, apply_move
from entropy import entropy_score

def solve(initial_state, capacity, max_nodes=100000):
    num_colors = len(set(c for tube in initial_state for c in tube))
    M_scale = num_colors * capacity * 1.0  # More aggressive scaling
    
    h0 = entropy_score(initial_state, capacity) * M_scale
    counter = 0
    open_set = [(h0, 0, counter, initial_state, [])]
    visited = {}
    nodes_explored = 0
    
    while open_set and nodes_explored < max_nodes:
        f, g, _, state, path = heapq.heappop(open_set)
        nodes_explored += 1
        
        c = canonical(state)
        if c in visited and visited[c] <= g:
            continue
        visited[c] = g
        
        if is_goal(state, capacity):
            print(f"Nodes explored: {nodes_explored}")
            return path
        
        # Prune if path is getting too long
        if g > num_colors * capacity * 2:
            continue
        
        for (i, j) in get_valid_moves(state, capacity):
            next_state = apply_move(state, i, j, capacity)
            nc = canonical(next_state)
            ng = g + 1
            
            if nc not in visited or visited[nc] > ng:
                nh = entropy_score(next_state, capacity) * M_scale
                counter += 1
                heapq.heappush(open_set, (ng + nh, ng, counter, next_state, path + [(i, j)]))
    
    print(f"Nodes explored: {nodes_explored} (limit reached)")
    return None
