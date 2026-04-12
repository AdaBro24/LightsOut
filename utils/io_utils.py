from typing import List, Dict, Any, Callable
from datetime import datetime
import os

from board import Board
from utils.perf import run_with_stats


def load_board_from_file(path: str) -> Board:
    #load a board from a 0/1 text file (example in example.txt)
    with open(path, 'r', encoding='utf-8') as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if not lines:
        raise ValueError('empty board file')

    rows: List[List[int]] = []
    for ln in lines:
        parts = ln.split()
        row = [int(p) for p in parts]

        
        if any(v not in (0, 1) for v in row):
            raise ValueError('board values must be 0 or 1')
        rows.append(row)

    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise ValueError('inconsistent row lengths')

    # set global board size and return Board
    Board.board_size = width
    return Board(rows)


def save_results_to_file(path: str, results: Dict[str, Any]):
    #write a compact results file

    lines: List[str] = []
    if results.get('input_file'):

        lines.append(f"Input file: {results['input_file']}")
    if results.get('solver'):
        lines.append(f"Solver: {results['solver']}")

    sol = results.get('solution')
    lines.append(f"Solution found: {sol is not None}")
    if sol:
        lines.append(f"Solution moves: {sol}")

    if results.get('elapsed') is not None:
        lines.append(f"Elapsed (s): {results['elapsed']:.6f}")
    if results.get('peak') is not None:

        peak = results['peak']
        lines.append(f"Peak (bytes): {peak} | {peak/1024:.2f} KiB")


    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def save_bulk_results(input_path: str, solvers: Dict[str, Callable], output_path: str = None) -> str:
    #load board from input_path, run solvers and write a combined results file.
    # load input and run each solver, capturing elapsed and peak memory
    board = load_board_from_file(input_path)
    results: Dict[str, Dict[str, Any]] = {}
    for name, fn in solvers.items():
        try:
            sol, elapsed, peak = run_with_stats(fn, board)
            results[name] = {'solution': sol, 'elapsed': elapsed, 'peak': peak}
        except Exception as e:

            results[name] = {'solution': None, 'elapsed': None, 'peak': None, 'error': str(e)}

    out = output_path or (input_path + '_all_results.txt')
    lines: List[str] = [f'Bulk results for: {input_path}', f'Generated: {datetime.utcnow().isoformat()} UTC', '']

    for name, info in results.items():
        lines.append(f'=== Solver: {name} ===')

        if 'error' in info:
            lines.append(f"Error: {info['error']}")
            lines.append('')
            continue


        sol = info.get('solution')

        lines.append(f'Solution found: {sol is not None}')
        if sol:
            lines.append(f'Solution moves: {sol}')
            b = board
            for x, y in sol:
                b = b.toggle(x, y)


        if info.get('elapsed') is not None:
            lines.append(f"Elapsed (s): {info['elapsed']:.6f}")
        if info.get('peak') is not None:
            p = info['peak']
            lines.append(f"Peak (bytes): {p} | {p/1024:.2f} KiB")

        lines.append('')

    os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return out
