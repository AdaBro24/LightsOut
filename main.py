from board import *
from bfs import bfs
from dfs import dfs



if __name__ == '__main__':

    start_grid = [
        [0, 0, 1,],
        [1, 0, 0,],
        [0, 0, 0]
    ]

    start_board = Board(start_grid)
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
            for i, (x, y) in enumerate(solution, 1):
                print(f"Move: {i}: toggle: ({x},{y}))")
                board = board.toggle(x, y)
                board.display()



