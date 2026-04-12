from board import Board

def depth_limited_search(board, limit, path, visited):
    # depth limited recursive search
    # return a path when goal found else None

    if board.is_goal():
        return path

    if limit == 0:
        return None

    for x in range(board.board_size):
        for y in range(board.board_size):
            new_board = board.toggle(x, y)
            state = tuple(tuple(row) for row in new_board.grid)

            if state not in visited:
                # mark state seen for this iteration
                visited.add(state)

                result = depth_limited_search(
                    new_board,
                    limit - 1,
                    path + [(x, y)],
                    visited,
                )

                if result is not None:
                    return result
    return None

def iterative_deepening(start_board, max_depth = 10):
    # increase depth limits until solution or max_depth
    for depth in range(max_depth + 1):

        visited = set()
        # record starting state so we dont revisit it in the depth search
        visited.add(tuple(tuple(row) for row in start_board.grid))

        result = depth_limited_search(start_board, depth, [], visited)

        if result is not None:
            return result

    return None
