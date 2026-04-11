from board import Board
from bfs import bfs
from dfs import dfs
from perf import run_with_stats

try:
    from gui import main as gui_main, TK_AVAILABLE
except Exception:
    gui_main = None
    TK_AVAILABLE = False


def run_textual(start_board: Board):
    print("start_board: ")
    start_board.display()

    algorithm = input("Choose an algorithm: 'bfs' or 'dfs':")
    match algorithm:
        case "bfs":
            solution, elapsed, peak = run_with_stats(bfs, start_board)

            if solution is None:
                print("There is no solution")
            else:
                print(f"Solution found in {len(solution)} moves")
                print("Moves:", solution)

            print(f"Time: {elapsed:.6f} s | Peak Python memory: {peak/1024:.2f} KiB")

            board = start_board
            if solution:
                for i, (x, y) in enumerate(solution, 1):
                    print(f"Move: {i}: toggle: ({x},{y}))")
                    board = board.toggle(x, y)
                    board.display()

        case "dfs":
            solution, elapsed, peak = run_with_stats(dfs, start_board)

            if solution is None:
                print("There is no solution")
            else:
                print(f"Solution found in {len(solution)} moves")
                print("Moves:", solution)

            print(f"Time: {elapsed:.6f} s | Peak Python memory: {peak/1024:.2f} KiB")

            board = start_board
            if solution:
                for i, (x, y) in enumerate(solution, start=1):
                    print(f"Move: {i}: toggle: ({x},{y}))")
                    board = board.toggle(x, y)
                    board.display()

        case _:
            print("wrong input")


if __name__ == '__main__':

    start_grid = [
        [0, 1, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
    ]

    start_board = Board(start_grid)

    if TK_AVAILABLE:
        choice = input("Choose interface: \n[0] GUI \n[1] CLI \n(default gui): ").strip().lower()
        if choice == '1':
            run_textual(start_board)
        else:
            try:
                gui_main(start_board)
            except Exception as e:
                print('Failed to launch GUI, falling back to CLI:', e)
                run_textual(start_board)
    else:
        run_textual(start_board)





