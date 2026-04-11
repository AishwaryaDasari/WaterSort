def print_initial(state):
    print("Initial state:")
    for ti, tube in enumerate(state):
        print(f"  T{ti}: {list(tube)}")
    print()

def print_move(move_number, i, j, pour_count, color, state):
    print(f"Move {move_number}: T{i} → T{j}  (pour {pour_count}×{color})")
    for ti, tube in enumerate(state):
        print(f"  T{ti}: {list(tube)}")
    print()

def print_solution(total_moves):
    print("─" * 40)
    print(f"Solved in {total_moves} moves.")
