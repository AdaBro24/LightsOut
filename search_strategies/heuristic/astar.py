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


def chase_lights_heuristic(board):
    # scan row by row and whenever a lit cell is found in row r, count a forced toggle in row r+1

    n = board.board_size
    # use a mutable copy so we dont alter the real board
    sim = [row[:] for row in board.grid]
    forced = 0
    for r in range(n - 1):
        for c in range(n):
            if sim[r][c] == 1:
                forced += 1

                for dr, dc in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nr, nc = r + 1 + dr, c + dc


                    if 0 <= nr < n and 0 <= nc < n:
                        sim[nr][nc] ^= 1
    # remaining lit cells in the last row need dedicated moves
    forced += sum(sim[n - 1])
    return forced


def gf2_heuristic(board):
    # gf2 heuristic: gaussian elimination to estimate min moves when feasible

    n = board.board_size
    num_cells = n * n

    # flatten board state to vector and build toggle matrix
    b = [board.grid[r][c] for r in range(n) for c in range(n)]
    A = [[0] * num_cells for _ in range(num_cells)]
    for r in range(n):
        for c in range(n):

            j = r * n + c
            for dr, dc in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < n and 0 <= nc < n:
                    A[nr * n + nc][j] = 1

    # form augmented matrix [A|b] and perform gaussian elim over gf(2)
    mat = [A[i][:] + [b[i]] for i in range(num_cells)]
    pivot_cols = []
    row_idx = 0
    for col in range(num_cells):
        pivot = None
        for r in range(row_idx, num_cells):
            if mat[r][col] == 1:
                pivot = r
                break
        if pivot is None:

            continue
        mat[row_idx], mat[pivot] = mat[pivot], mat[row_idx]
        pivot_cols.append(col)

        for r in range(num_cells):
            if r != row_idx and mat[r][col] == 1:
                mat[r] = [(mat[r][k] ^ mat[row_idx][k]) for k in range(num_cells + 1)]
        row_idx += 1

    # check inconsistency
    for r in range(num_cells):
        if all(mat[r][c] == 0 for c in range(num_cells)) and mat[r][num_cells] == 1:
            return math.inf

    pivot_set = set(pivot_cols)
    free_vars = [c for c in range(num_cells) if c not in pivot_set]
    particular = [0] * num_cells
    for i, col in enumerate(pivot_cols):
        particular[col] = mat[i][num_cells]

    #if too many free vars, fallback to cheap heuristic
    num_free = len(free_vars)
    if num_free > 20:
        return default_heuristic(board)

    min_weight = sum(particular)
    for mask in range(1, 1 << num_free):

        null_vec = [0] * num_cells
        for bit, fv in enumerate(free_vars):
            if mask & (1 << bit):
                null_vec[fv] = 1

        candidate = particular[:]

        for i, col in enumerate(pivot_cols):
            val = mat[i][num_cells]

            for bit, fv in enumerate(free_vars):
                val ^= mat[i][fv] * null_vec[fv]

            candidate[col] = val
            
        for fv in free_vars:

            candidate[fv] = null_vec[fv]
        weight = sum(candidate)
        if weight < min_weight:
            min_weight = weight

    return min_weight


def isolated_lights_heuristic(board):
    # isolated lights need dedicated toggles, gives admissible lower bound
    n = board.board_size
    count = 0
    for r in range(n):
        for c in range(n):

            if board.grid[r][c] == 1:

                has_lit_neighbor = any(
                    board.grid[r + dr][c + dc] == 1
                    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    if 0 <= r + dr < n and 0 <= c + dc < n
                )
                if not has_lit_neighbor:
                    count += 1
    return count


def combined_heuristic(board):
    return max(
        default_heuristic(board),
        chase_lights_heuristic(board),
        isolated_lights_heuristic(board),
        gf2_heuristic(board),
    )

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

    # choose default heuristic if none provided
    if heuristic is None:
        heuristic = default_heuristic

    start_state = board_to_state(start_board)
    if start_board.is_goal():
        return []

    open_heap: List[Tuple[float, int, State]] = []  # (f, counter, state)
    g_score = {start_state: 0}
    came_from = {start_state: (None, None)}

    counter = 0
    f0 = weight * heuristic(start_board)
    heappush(open_heap, (f0, counter, start_state))

    expansions = 0
    visited = set()

    #map states to board objects so we can expand quickly
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
        # expand neighbors by toggling every button
        for x in range(current_board.board_size):
            for y in range(current_board.board_size):
                neighbor_board = current_board.toggle(x, y)
                neighbor_state = board_to_state(neighbor_board)
                tentative_g = g_current + 1

                if tentative_g < g_score.get(neighbor_state, math.inf):
                    # found a better path to neighbor
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
