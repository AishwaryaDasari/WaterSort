from state import is_goal
from moves import get_valid_moves, apply_move
from entropy import entropy_score

def solve_greedy(initial_state, capacity, max_moves=1000):
    state = initial_state
    path = []
    visited = {}
    backtrack_limit = 10
    
    for step in range(max_moves):
        if is_goal(state, capacity):
            return path
        
        state_key = tuple(sorted(state))
        
        # Track how many times we've seen this state
        if state_key in visited:
            visited[state_key] += 1
            if visited[state_key] > backtrack_limit:
                return None
        else:
            visited[state_key] = 1
        
        valid_moves = get_valid_moves(state, capacity)
        if not valid_moves:
            return None
        
        # Evaluate all moves
        move_scores = []
        for move in valid_moves:
            next_state = apply_move(state, move[0], move[1], capacity)
            e = entropy_score(next_state, capacity)
            next_key = tuple(sorted(next_state))
            # Penalize revisiting states
            penalty = visited.get(next_key, 0) * 0.05
            move_scores.append((e + penalty, move, next_state))
        
        move_scores.sort()
        
        # Try alternative moves when stuck
        choice_idx = min(visited[state_key] - 1, len(move_scores) - 1)
        best_entropy, best_move, next_state = move_scores[choice_idx]
        
        path.append(best_move)
        state = next_state
    
    return None
