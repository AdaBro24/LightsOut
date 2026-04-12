from typing import Optional, List, Tuple, Callable
from board import Board


# heuristic should accept a Board and return an int score (lower better)
def greedy(start_board, max_iters=None, heuristic=None):
    # if no heuristic provided, use simple lit cell count
    def lit_count(b):
        return sum(cell for row in b.grid for cell in row)

    score_fn = heuristic if heuristic is not None else lit_count

    n = start_board.board_size
    if max_iters is None:
        max_iters = n * n * 10

    def board_state(b: Board):
        return tuple(tuple(row) for row in b.grid)

    board = start_board
    path: List[Tuple[int, int]] = []
    visited = {board_state(board)}

    for _ in range(max_iters):
        if board.is_goal():
            return path

        #evaluate all possible single toggles using score_fn
        candidates = []  # (score, state, move, board)
        for x in range(n):
            for y in range(n):
                nb = board.toggle(x, y)
                ns = board_state(nb)
                candidates.append((score_fn(nb), ns, (x, y), nb))

        candidates.sort(key=lambda t: t[0])

        chosen = None
        for sc, ns, move, nb in candidates:
            if ns not in visited:
                chosen = (ns, move, nb)
                break

        if chosen is None:
            return None

        ns, move, nb = chosen
        path.append(move)
        board = nb
        visited.add(ns)

    return None
