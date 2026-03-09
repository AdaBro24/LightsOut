from board import Board
from bfs import bfs
from dfs import dfs

try:
    # optional GUI module
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
            solution = bfs(start_board)

            if solution is None:
                print("There is no solution")
            else:
                print(f"Solution found in {len(solution)} moves")
                print("Moves:", solution)

            board = start_board
            for i, (x, y) in enumerate(solution, 1):
                print(f"Move: {i}: toggle: ({x},{y}))")
                board = board.toggle(x, y)
                board.display()

        case "dfs":
            solution = dfs(start_board)

            if solution is None:
                print("There is no solution")
            else:
                print(f"Solution found in {len(solution)} moves")
                print("Moves:", solution)

            board = start_board
            for i, (x, y) in enumerate(solution, start=1):
                print(f"Move: {i}: toggle: ({x},{y}))")
                board = board.toggle(x, y)
                board.display()

        case _:
            print("wrong input")


if __name__ == '__main__':

    start_grid = [
        [0, 0, 1,],
        [1, 0, 0,],
        [0, 0, 0]
    ]

    start_board = Board(start_grid)

    # Let user choose GUI or CLI when possible
    if TK_AVAILABLE:
        choice = input("Choose interface: 'gui' or 'cli' (default cli): ").strip().lower()
        if choice == 'gui':
            try:
                gui_main(start_board)
            except Exception as e:
                print('Failed to launch GUI, falling back to CLI:', e)
                run_textual(start_board)
        else:
            run_textual(start_board)
    else:
        run_textual(start_board)





