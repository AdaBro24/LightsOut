from heapq import heappush, heappop

def ufc(start_board):

    pq = []
    visited = set()
    counter = 0

    heappush(pq, (0, counter, start_board, []))

    visited.add(tuple(tuple(row) for row in start_board.grid))

    while pq:
        cost, _, board, path = heappop(pq)

        if board.is_goal():
            return path

        for x in range(board.board_size):
            for y in range(board.board_size):

                new_board = board.toggle(x, y)
                state = tuple(tuple(row) for row in new_board.grid)

                if state not in visited:
                    visited.add(state)

                    counter += 1
                    new_cost = cost + 1

                    heappush(pq, (new_cost, counter, new_board, path + [(x, y)]))

    return None