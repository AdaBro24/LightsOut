try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, filedialog
    TK_AVAILABLE = True
except Exception:
    tk = None
    messagebox = None
    simpledialog = None
    TK_AVAILABLE = False

import random

from board import Board
from search_strategies.uninformed.bfs import bfs
from search_strategies.uninformed.dfs import dfs
from search_strategies.heuristic.astar import (
    astar,
    weighted_astar,
    default_heuristic,
    chase_lights_heuristic,
    isolated_lights_heuristic,
    combined_heuristic,
    gf2_heuristic,
)
from search_strategies.heuristic.greedy import greedy
from search_strategies.uninformed.iterative_deepening import iterative_deepening
from search_strategies.uninformed.ufc import ufc
from utils.perf import run_with_stats
from utils.io_utils import load_board_from_file, save_results_to_file, save_bulk_results


if TK_AVAILABLE:
    class LightsOutGUI:
        ROUND_SECONDS = 180

        def __init__(self, master, start_board: Board = None):
            self.master = master
            self.board_size = Board.board_size
            self.start_board = start_board or Board([[0]*self.board_size for _ in range(self.board_size)])
            self.board = self.start_board
            self.hint_move = None
            self.hints_used = 0
            self.points = 0
            self.remaining_seconds = self.ROUND_SECONDS
            self.timer_job = None
            self.solver_used_in_round = False
            self.last_results = None
            self.input_file = None

            master.title('Lights Out (project_adam)')

            self.frame = tk.Frame(master)
            self.frame.pack(padx=10, pady=10)

            self.buttons = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
            for r in range(self.board_size):
                for c in range(self.board_size):
                    b = tk.Button(self.frame, width=4, height=2, command=lambda r=r, c=c: self.on_press(r, c))
                    b.grid(row=r, column=c, padx=2, pady=2)
                    self.buttons[r][c] = b

            ctrl = tk.Frame(master)
            ctrl.pack(pady=6)

            tk.Button(ctrl, text='Solve', command=self.on_solve).grid(row=0, column=0, padx=4)
            tk.Button(ctrl, text='Reset Board', command=self.on_reset).grid(row=0, column=1, padx=4)
            tk.Button(ctrl, text='Quit', command=master.destroy).grid(row=0, column=2, padx=4)
            tk.Button(ctrl, text='Difficulty', command=self.choose_difficulty).grid(row=0, column=3, padx=4)
            tk.Button(ctrl, text='Hint', command=self.on_hint).grid(row=0, column=4, padx=4)
            tk.Button(ctrl, text='Load', command=self.on_load_file).grid(row=0, column=5, padx=4)


            self.status = tk.Label(master, text='')
            self.status.pack(pady=(4,0))
            self.timer_label = tk.Label(master, text='')
            self.timer_label.pack(pady=(2, 0))

            #self.start_new_round(randomize=True, restart_timer=True)
            self.choose_difficulty()
            self.refresh()

        def format_time(self, total_seconds: int) -> str:
            mins = total_seconds // 60
            secs = total_seconds % 60
            return f'{mins:02d}:{secs:02d}'

        def generate_random_board(self, presses: int = 10) -> Board:
            board = Board([[0] * self.board_size for _ in range(self.board_size)])
            for _ in range(presses):
                r = random.randrange(self.board_size)
                c = random.randrange(self.board_size)
                board = board.toggle(r, c)
            return board

        def start_new_round(self, randomize: bool = True, restart_timer: bool = True):
            self.solver_used_in_round = False
            self.hint_move = None
            if randomize:
                self.board = self.generate_random_board()
            else:
                self.board = self.start_board
            if restart_timer:
                self.remaining_seconds = self.ROUND_SECONDS
            if self.timer_job is not None:
                self.master.after_cancel(self.timer_job)
                self.timer_job = None
            self.tick_timer()

        def choose_difficulty(self):
            choice = simpledialog.askstring(
                'Difficulty',
                "Choose difficulty: 'easy', 'medium', 'hard'",
                initialvalue="medium"
            )

            if not choice:
                return

            choice = choice.strip().lower()

            if choice == 'easy':
                size = 3
            elif choice == 'medium':
                size = 4
            elif choice == 'hard':
                size = 5
            else:
                messagebox.showerror('Error', 'Invalid Difficulty')
                return

            Board.board_size = size
            self.board_size = size

            self.rebuild_board()

        def rebuild_board(self):
            for row in self.buttons:
                for btn in row:
                    btn.destroy()

            self.buttons = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]

            for r in range(self.board_size):
                for c in range(self.board_size):
                    b = tk.Button(
                        self.frame,
                        width=4,
                        height=2,
                        command=lambda r=r, c=c: self.on_press(r, c)
                    )
                    b.grid(row=r, column=c, padx=2, pady=2)
                    self.buttons[r][c] = b

            self.start_new_round(randomize=True, restart_timer=True)
            self.refresh()


        def tick_timer(self):
            if self.board.is_goal():
                self.timer_job = None
                return

            if self.remaining_seconds <= 0:
                self.timer_label.config(text='Time: 00:00')
                messagebox.showinfo('Time', "Time's up! New board generated.")
                self.start_new_round(randomize=True, restart_timer=True)
                self.refresh()
                return

            self.timer_label.config(text=f'Time: {self.format_time(self.remaining_seconds)}')
            self.remaining_seconds -= 1
            self.timer_job = self.master.after(1000, self.tick_timer)

        def color_for(self, val: int) -> str:
            return '#ffd54f' if val else '#9e9e9e'

        def refresh(self):
            for r in range(self.board_size):
                for c in range(self.board_size):
                    val = self.board.grid[r][c]
                    b = self.buttons[r][c]
                    b.config(bg=self.color_for(val), activebackground=self.color_for(val))
                    if self.hint_move == (r, c):
                        b.config(relief='solid', bd=4)
                    else:
                        b.config(relief='raised', bd=1)
            solved = self.board.is_goal()
            if solved:
                self.status.config(text=f'Solved | Points: {self.points} | Hints used: {self.hints_used}')
            else:
                self.status.config(text=f'Not solved | Points: {self.points} | Hints used: {self.hints_used}')

        def finish_round_if_solved(self):
            if not self.board.is_goal():
                return
            if not self.solver_used_in_round:
                self.points += 1
                messagebox.showinfo('Victory', f'Level complete! +1 point. Total points: {self.points}')
            else:
                messagebox.showinfo('Victory', 'Level complete, but no points awarded after using Solve.')
            self.start_new_round(randomize=True, restart_timer=False)
            self.refresh()

        def on_press(self, r: int, c: int):
            if self.remaining_seconds <= 0:
                return
            self.hint_move = None
            self.board = self.board.toggle(r, c)
            self.refresh()
            self.finish_round_if_solved()

        def on_reset(self):
            #new random board, points are preserved.
            self.start_new_round(randomize=True, restart_timer=False)
            self.refresh()

        def on_load_file(self):
            try:
                path = filedialog.askopenfilename(filetypes=[('Text files','*.txt'), ('All','*.*')])
            except Exception:
                #input if filedialog not available
                path = input('Path to puzzle file: ').strip()

            if not path:
                return

            try:
                board = load_board_from_file(path)
            except Exception as e:
                messagebox.showerror('Load', f'Failed to load board: {e}')
                return

            # apply loaded board: recreate buttons for new size and set board
            self.input_file = path
            self.start_board = board
            self.board = board
            self.board_size = Board.board_size

            # destroy existing buttons
            for row in self.buttons:
                for btn in row:
                    try:
                        btn.destroy()
                    except Exception:
                        pass

            self.buttons = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
            for r in range(self.board_size):
                for c in range(self.board_size):
                    b = tk.Button(
                        self.frame,
                        width=4,
                        height=2,
                        command=lambda r=r, c=c: self.on_press(r, c)
                    )
                    b.grid(row=r, column=c, padx=2, pady=2)
                    self.buttons[r][c] = b

            self.refresh()

            # immediately run all solvers and write combined results file
            try:
                solvers = {
                    'bfs': bfs,
                    'dfs': dfs,
                    'astar': astar,
                    'weighted_astar_w1.5': (lambda b: weighted_astar(b, 1.5)),
                    'greedy': greedy,
                    'iddfs_d10': (lambda b: iterative_deepening(b, 10)),
                    'ufc': ufc,
                }
                out_path = save_bulk_results(path, solvers)
                messagebox.showinfo('Load', f'Loaded board and saved bulk results to:\n{out_path}')
            except Exception as e:
                messagebox.showerror('Bulk run', f'Failed to run solvers and save results: {e}')

        

        def on_hint(self):
            if self.board.is_goal():
                messagebox.showinfo('Hint', 'Board is already solved.')
                return

            solution, elapsed, peak = run_with_stats(astar, self.board)
            if solution is None:
                solution, elapsed2, peak2 = run_with_stats(bfs, self.board)
                elapsed = elapsed2
                peak = peak2

            if not solution:
                self.hint_move = None
                messagebox.showinfo('Hint', 'No hint available for this state.')
                self.refresh()
                return

            self.hints_used += 1
            self.hint_move = solution[0]
            self.refresh()
            r, c = self.hint_move

            # store last hint stats so user can save them if desired
            self.last_results = {
                'input_file': getattr(self, 'input_file', None),
                'solver': 'hint',
                'solution': solution,
                'elapsed': elapsed,
                'peak': peak,
                'final_board': None,
                'notes': 'Hint generated (first move)'
            }

        def on_solve(self):
            prompt = "Choose solver: 'bfs', 'dfs', 'iddfs' or 'ufc', 'greedy', 'astar', or 'wastar' (weighted A*)."
            algo = simpledialog.askstring('Solver', prompt, initialvalue='bfs')

            if not algo:
                return

            algo = algo.strip().lower()
            self.solver_used_in_round = True
            self.hint_move = None

            if algo == 'bfs':
                solution, elapsed, peak = run_with_stats(bfs, self.board)

            elif algo == 'dfs':
                solution, elapsed, peak = run_with_stats(dfs, self.board)
            elif algo == 'astar':
                # ask which heuristic to use for A*
                heur = simpledialog.askstring('Heuristic', "Choose heuristic: 'default', 'chase', 'isolated', 'combined', 'gf2'", initialvalue='default')
                heur_name = (heur or 'default').strip().lower()
                heur_map = {
                    'default': default_heuristic,
                    'chase': chase_lights_heuristic,
                    'isolated': isolated_lights_heuristic,
                    'combined': combined_heuristic,
                    'gf2': gf2_heuristic,
                }
                heuristic_fn = heur_map.get(heur_name, default_heuristic)
                solution, elapsed, peak = run_with_stats(astar, self.board, heuristic_fn)
            elif algo in ('wastar', 'weighted', 'weighted_astar', 'weightedastar'):
                weight = simpledialog.askfloat('Weighted A*', 'Weight:', initialvalue=1.5, minvalue=1.0)
                if weight is None:
                    return
                # choose heuristic for weighted A*
                heur = simpledialog.askstring('Heuristic', "Choose heuristic: 'default', 'chase', 'isolated', 'combined', 'gf2'", initialvalue='default')
                heur_name = (heur or 'default').strip().lower()
                heur_map = {
                    'default': default_heuristic,
                    'chase': chase_lights_heuristic,
                    'isolated': isolated_lights_heuristic,
                    'combined': combined_heuristic,
                    'gf2': gf2_heuristic,
                }
                heuristic_fn = heur_map.get(heur_name, default_heuristic)
                solution, elapsed, peak = run_with_stats(weighted_astar, self.board, weight, heuristic_fn)
            elif algo == 'greedy':
                heur = simpledialog.askstring('Heuristic', "Choose heuristic: 'default', 'chase', 'isolated', 'combined', 'gf2'", initialvalue='default')
                heur_name = (heur or 'default').strip().lower()
                heur_map = {
                    'default': default_heuristic,
                    'chase': chase_lights_heuristic,
                    'isolated': isolated_lights_heuristic,
                    'combined': combined_heuristic,
                    'gf2': gf2_heuristic,
                }
                heuristic_fn = heur_map.get(heur_name, None)
                solution, elapsed, peak = run_with_stats(greedy, self.board, None, heuristic_fn)
            elif algo == 'iddfs':

                max_depth = simpledialog.askinteger(
                    'Depth',
                    'Maximum search depth:',
                    initialvalue=10,
                    minvalue=1,
                    maxvalue=50
                )

                if max_depth is None:
                    return

                solution, elapsed, peak = run_with_stats(iterative_deepening, self.board, max_depth)

            elif algo == 'ufc':
                solution, elapsed, peak = run_with_stats(ufc, self.board)
            else:
                messagebox.showerror('Solver', "Unknown solver: use 'bfs', 'dfs', 'iddfs', 'ufc', 'astar' or 'wastar'")
                return
            if solution is None:
                messagebox.showinfo('Solve', 'There is no solution')
                return

            apply_now = messagebox.askyesno(
                'Apply solution',
                f'Solution found with {len(solution)} moves. \nTime: {elapsed:.6f} s\nPeak memory: {peak/1024:.2f} KiB. Apply with animation?'
            )

            if apply_now:
                self.animate_solution(solution)
            else:
                messagebox.showinfo('Solution', f'Moves: {solution}')
            # compute final board after applying solution (without mutating current board)
            final_board = self.board
            if solution:
                # apply moves to a copy
                b = final_board
                for (x, y) in solution:
                    b = b.toggle(x, y)
                final_board = b

            # store last solve stats for save
            self.last_results = {
                'input_file': getattr(self, 'input_file', None),
                'solver': algo,
                'solution': solution,
                'elapsed': elapsed,
                'peak': peak,
                'final_board': final_board,
            }

        def animate_solution(self, solution, delay=400):
            # animate applying each toggle in sequence using after
            if not solution:
                messagebox.showinfo('Solve', 'Done. Board solved?' )
                self.finish_round_if_solved()
                return

            move = solution[0]
            self.board = self.board.toggle(move[0], move[1])
            self.refresh()

            self.master.after(delay, lambda: self.animate_solution(solution[1:], delay))


    def main(start_board: Board = None):
        try:
            root = tk.Tk()
        except Exception as e:
            print('Unable to start GUI:', e)
            return
        app = LightsOutGUI(root, start_board=start_board)
        root.mainloop()

else:
    def main(start_board: Board = None):
        print('Tkinter is not available. Falling back to CLI for project_adam.')
        #if tkinter missing, run cli
        try:
            import main as textual_main
            if hasattr(textual_main, 'main'):
                textual_main.main()
        except Exception:
            print('Could not invoke textual main.')
