#!/usr/bin/env python3
"""Simple tests for Water Sort solver components"""

from state import canonical, is_goal, is_complete
from moves import get_top_run, apply_move, get_valid_moves
from heuristic import heuristic, fragmentation_score, transition_score
from solver import solve

def test_state():
    print("Testing state.py...")
    
    # Canonical form
    s1 = (('R', 'B'), ('G', 'Y'))
    s2 = (('G', 'Y'), ('R', 'B'))
    assert canonical(s1) == canonical(s2), "Canonical form failed"
    
    # Goal detection
    goal = (('R', 'R'), ('B', 'B'), ())
    assert is_goal(goal, 2), "Goal detection failed"
    
    partial = (('R',), ('B', 'B'), ())
    assert not is_goal(partial, 2), "Partial fill should not be goal"
    
    # Complete tube
    assert is_complete(('R', 'R', 'R'), 3), "Complete tube check failed"
    assert not is_complete(('R', 'B', 'R'), 3), "Mixed tube should not be complete"
    
    print("PASS: state.py tests passed")

def test_moves():
    print("Testing moves.py...")
    
    # Top run
    assert get_top_run(('R', 'B', 'G', 'G')) == ('G', 2), "Top run failed"
    assert get_top_run(()) == (None, 0), "Empty tube top run failed"
    
    # Apply move (multi-layer pour)
    s = (('R', 'B', 'G', 'G'), ('G', 'R'), ())
    result = apply_move(s, 0, 1, 4)
    assert result[0] == ('R', 'B'), "Source not updated correctly"
    assert result[1] == ('G', 'R', 'G', 'G'), "Destination not updated correctly"
    
    # Valid moves
    state = (('R', 'B'), ('B', 'R'), ())
    moves = get_valid_moves(state, 2)
    assert len(moves) > 0, "Should have valid moves"
    
    print("PASS: moves.py tests passed")

def test_heuristic():
    print("Testing heuristic.py...")
    
    # Heuristic on goal state
    goal = (('R', 'R', 'R'), ('B', 'B', 'B'), ())
    assert heuristic(goal) == 0, "Heuristic should be 0 on goal"
    
    # Fragmentation
    s = (('R', 'G'), ('R', 'B'), ())
    assert fragmentation_score(s) == 1, "R in 2 tubes should give score 1"
    
    # Transitions
    s2 = (('R', 'G'),)
    assert transition_score(s2) == 1, "One color change should give score 1"
    
    s3 = (('R', 'R', 'R'),)
    assert transition_score(s3) == 0, "Uniform tube should have 0 transitions"
    
    print("PASS: heuristic.py tests passed")

def test_solver():
    print("Testing solver.py...")
    
    # Trivial puzzle
    state = (('R', 'B'), ('B', 'R'), ())
    path = solve(state, 2)
    assert path is not None, "Should find solution"
    assert len(path) <= 4, f"Expected <= 4 moves, got {len(path)}"
    
    # Baseline puzzle
    state = (
        ('R', 'B', 'G', 'Y'),
        ('G', 'R', 'Y', 'B'),
        ('Y', 'G', 'B', 'R'),
        ('B', 'Y', 'R', 'G'),
        (),
    )
    path = solve(state, 4)
    assert path is not None, "Should find solution"
    assert len(path) == 13, f"Expected 13 moves, got {len(path)}"
    
    # Already solved
    state = (('R', 'R'), ('B', 'B'), ())
    path = solve(state, 2)
    assert path == [], "Already solved should return empty path"
    
    print("PASS: solver.py tests passed")

if __name__ == "__main__":
    test_state()
    test_moves()
    test_heuristic()
    test_solver()
    print("\nAll tests passed!")
