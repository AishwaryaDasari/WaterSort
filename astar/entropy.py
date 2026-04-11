import math
from collections import defaultdict

def color_distribution(state):
    dist = defaultdict(lambda: defaultdict(int))
    for i, tube in enumerate(state):
        for layer in tube:
            dist[layer][i] += 1
    return dist

def shannon_entropy_per_color(state):
    dist = color_distribution(state)
    result = {}
    for color, tube_counts in dist.items():
        total = sum(tube_counts.values())
        h = 0.0
        for count in tube_counts.values():
            if count > 0:
                p = count / total
                h -= p * math.log2(p)
        result[color] = h
    return result

def normalized_shannon_entropy(state, num_tubes):
    per_color = shannon_entropy_per_color(state)
    if not per_color:
        return 0.0
    H_total = sum(per_color.values())
    H_max = len(per_color) * math.log2(max(num_tubes, 2))
    return H_total / H_max if H_max > 0 else 0.0

def vertical_entropy(state, capacity):
    if capacity <= 1:
        return 0.0
    total_transitions = 0
    filled_tubes = [t for t in state if len(t) > 1]
    if not filled_tubes:
        return 0.0
    max_transitions = len(filled_tubes) * (capacity - 1)
    for tube in filled_tubes:
        for k in range(len(tube) - 1):
            if tube[k] != tube[k + 1]:
                total_transitions += 1
    return total_transitions / max_transitions

def empty_ratio(state, num_tubes):
    empty_count = sum(1 for t in state if len(t) == 0)
    return empty_count / num_tubes if num_tubes > 0 else 0.0

def entropy_score(state, capacity, alpha=0.6, beta=0.4, gamma=0.1):
    num_tubes = len(state)
    h_norm = normalized_shannon_entropy(state, num_tubes)
    v_score = vertical_entropy(state, capacity)
    empty_r = empty_ratio(state, num_tubes)
    E = alpha * h_norm + beta * v_score - gamma * empty_r
    return max(0.0, E)
