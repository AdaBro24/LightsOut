from board import Board
from bfs import bfs
from dfs import dfs
from perf import run_with_stats
from io_utils import load_board_from_file, save_results_to_file, save_bulk_results
from cli import run_textual

try:
    from gui import main as gui_main, TK_AVAILABLE
except Exception:
    gui_main = None
    TK_AVAILABLE = False


if __name__ == '__main__':

    start_board = None


    if TK_AVAILABLE:
        choice = input("Choose interface: \n[0] GUI \n[1] CLI \n(default gui): ").strip().lower()
        if choice == '1':
            run_textual(start_board)
        else:
            try:
                gui_main(start_board)
            except Exception as e:
                print('Failed to launch GUI, falling back to CLI:', e)
                run_textual(start_board)
    else:
        run_textual(start_board)





