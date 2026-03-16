from heapq import heappush, heappop
from typing import Callable, List, Optional, Tuple, Dict
import math

from board import Board

State = Tuple[Tuple[int, ...], ...]
Move = Tuple[int, int]


def board_to_state(board):
    return tuple(tuple(row) for row in board.grid)


def default_heuristic(board):
    # number of lit up cells 
    cnt = sum(cell for row in board.grid for cell in row)
    if cnt == 0:
        return 0
    # cause each move lights up at most 5 lights
    return math.ceil(cnt / 5)

def reconstruct_path(came_from, current):
    path= []
    while True:
        prev, move = came_from.get(current, (None, None))
        if prev is None or move is None:
            break
        path.append(move)
        current = prev
    path.reverse()
    return path


def astar(start_board, heuristic=None, weight=1.0, max_expansions=None):

    if heuristic is None:
        heuristic = default_heuristic

    start_state = board_to_state(start_board)
    if start_board.is_goal():
        return []

    open_heap: List[Tuple[float, int, State]] = []  # (f, counter, state)
    g_score= {start_state: 0}
    came_from = {start_state: (None, None)}

    counter = 0
    f0 = weight * heuristic(start_board)
    heappush(open_heap, (f0, counter, start_state))

    expansions = 0
    visited = set()

    state_to_board = {start_state: start_board}

    while open_heap:
        f, _, current = heappop(open_heap)
        current_board = state_to_board[current]

        if current_board.is_goal():
            return reconstruct_path(came_from, current)

        if current in visited:
            continue
        visited.add(current)

        expansions += 1
        if max_expansions is not None and expansions > max_expansions:
            return None

        g_current = g_score.get(current, 0)
        for x in range(current_board.board_size):
            for y in range(current_board.board_size):
                neighbor_board = current_board.toggle(x, y)
                neighbor_state = board_to_state(neighbor_board)
                tentative_g = g_current + 1

                if tentative_g < g_score.get(neighbor_state, math.inf):
                    g_score[neighbor_state] = tentative_g
                    came_from[neighbor_state] = (current, (x, y))
                    state_to_board[neighbor_state] = neighbor_board
                    h = heuristic(neighbor_board)
                    f_score = tentative_g + weight * h
                    counter += 1
                    heappush(open_heap, (f_score, counter, neighbor_state))

    return None


def weighted_astar(start_board, weight, heuristic=None, max_expansions= None):
    return astar(start_board, heuristic=heuristic, weight=weight, max_expansions=max_expansions)


