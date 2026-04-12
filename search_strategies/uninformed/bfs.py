from collections import deque

def bfs(start_board):

    queue = deque()
    visited = set()

    queue.append((start_board, []))

    visited.add(tuple(tuple(row) for row in start_board.grid)) # changing set into tuple, cause we cant store lists in set

    while queue:
        board, path = queue.popleft()

        if board.is_goal():
            return path

        for x in range(board.board_size):
            for y in range(board.board_size):
                new_board = board.toggle(x,y)
                state = tuple(tuple(row) for row in new_board.grid)

                if state not in visited:
                    visited.add(state)
                    queue.append((new_board, path + [(x,y)]))

    return None
