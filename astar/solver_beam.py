from state import is_goal, canonical
from moves import get_valid_moves, apply_move
from entropy import entropy_score
import random

def solve_beam(initial_state, capacity, beam_width=5, max_depth=200):
    """Beam search: explore multiple paths simultaneously"""
    
    beam = [(entropy_score(initial_state, capacity), initial_state, [])]
    visited = set()
    
    for depth in range(max_depth):
        if not beam:
            return None
        
        # Check if any path reached goal
        for _, state, path in beam:
            if is_goal(state, capacity):
                print(f"Solved at depth {depth}")
                return path
        
        # Generate all successors
        candidates = []
        for _, state, path in beam:
            state_key = canonical(state)
            if state_key in visited:
                continue
            visited.add(state_key)
            
            for (i, j) in get_valid_moves(state, capacity):
                next_state = apply_move(state, i, j, capacity)
                next_key = canonical(next_state)
                if next_key not in visited:
                    e = entropy_score(next_state, capacity)
                    candidates.append((e, next_state, path + [(i, j)]))
        
        if not candidates:
            return None
        
        # Keep best beam_width candidates
        candidates.sort()
        beam = candidates[:beam_width]
        
        if depth % 10 == 0:
            print(f"Depth {depth}, beam size: {len(beam)}, best entropy: {beam[0][0]:.4f}")
    
    return None
