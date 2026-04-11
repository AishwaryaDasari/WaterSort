from collections import defaultdict

def fragmentation_score(state):
    color_tubes = defaultdict(set)
    for tube_idx, tube in enumerate(state):
        for layer in tube:
            color_tubes[layer].add(tube_idx)
    return sum(len(tubes) - 1 for tubes in color_tubes.values())

def transition_score(state):
    total = 0
    for tube in state:
        for k in range(1, len(tube)):
            if tube[k] != tube[k - 1]:
                total += 1
    return total

def heuristic(state):
    return fragmentation_score(state) + transition_score(state)
