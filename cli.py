from board import Board
from bfs import bfs
from dfs import dfs
from perf import run_with_stats
from io_utils import save_results_to_file


def run_textual(start_board: Board = None, input_file: str = None):
    if start_board is None:
        start_grid = [
            [0, 1, 0, 1],
            [0, 0, 0, 1],
            [0, 0, 1, 1],
            [0, 0, 1, 0],
        ]
        start_board = Board(start_grid)

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

            print(f"Time: {elapsed:.6f} s | Peak memory: {peak/1024:.2f} KiB")

            board = start_board
            if solution:
                for i, (x, y) in enumerate(solution, 1):
                    print(f"Move: {i}: toggle: ({x},{y}))")
                    board = board.toggle(x, y)
                    board.display()

            save_choice = input('Save results to file? (y/N): ').strip().lower()
            if save_choice == 'y':
                path = input('Path to save results (e.g. results.txt): ').strip()
                results = {
                    'input_file': input_file,
                    'solver': 'bfs',
                    'solution': solution,
                    'elapsed': elapsed,
                    'peak': peak,
                    'final_board': board,
                }
                try:
                    save_results_to_file(path, results)
                    print('Results saved to', path)
                except Exception as e:
                    print('Failed to save results:', e)

        case "dfs":
            solution, elapsed, peak = run_with_stats(dfs, start_board)

            if solution is None:
                print("There is no solution")
            else:
                print(f"Solution found in {len(solution)} moves")
                print("Moves:", solution)

            print(f"Time: {elapsed:.6f} s | Peak memory: {peak/1024:.2f} KiB")

            board = start_board
            if solution:
                for i, (x, y) in enumerate(solution, start=1):
                    print(f"Move: {i}: toggle: ({x},{y}))")
                    board = board.toggle(x, y)
                    board.display()

            save_choice = input('Save results to file? (y/N): ').strip().lower()
            if save_choice == 'y':
                path = input('Path to save results (e.g. results.txt): ').strip()
                results = {
                    'input_file': input_file,
                    'solver': 'dfs',
                    'solution': solution,
                    'elapsed': elapsed,
                    'peak': peak,
                    'final_board': board,
                }
                try:
                    save_results_to_file(path, results)
                    print('Results saved to', path)
                except Exception as e:
                    print('Failed to save results:', e)

        case _:
            print("wrong input")
