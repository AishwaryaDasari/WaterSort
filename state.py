def canonical(state):
    return tuple(sorted(state))

def is_goal(state, capacity):
    for tube in state:
        if len(tube) == 0:
            continue
        if len(tube) != capacity or len(set(tube)) != 1:
            return False
    return True

def is_complete(tube, capacity):
    return len(tube) == capacity and len(set(tube)) == 1
