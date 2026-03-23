try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    TK_AVAILABLE = True
except Exception:
    tk = None
    messagebox = None
    simpledialog = None
    TK_AVAILABLE = False

import random

from board import Board
from bfs import bfs
from dfs import dfs
from astar import astar, weighted_astar
from iterative_deepening import iterative_deepening
from ufc import ufc


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
            tk.Button(ctrl, text='Hint', command=self.on_hint).grid(row=0, column=1, padx=4)
            tk.Button(ctrl, text='Reset Board', command=self.on_reset).grid(row=0, column=2, padx=4)
            tk.Button(ctrl, text='Quit', command=master.destroy).grid(row=0, column=3, padx=4)

            self.status = tk.Label(master, text='')
            self.status.pack(pady=(4,0))
            self.timer_label = tk.Label(master, text='')
            self.timer_label.pack(pady=(2, 0))

            self.start_new_round(randomize=True, restart_timer=True)
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

        def on_hint(self):
            if self.board.is_goal():
                messagebox.showinfo('Hint', 'Board is already solved.')
                return

            # A* first option. BFS if doesnt work
            solution = astar(self.board)
            if solution is None:
                solution = bfs(self.board)

            if not solution:
                self.hint_move = None
                messagebox.showinfo('Hint', 'No hint available for this state.')
                self.refresh()
                return

            self.hints_used += 1
            self.hint_move = solution[0]
            self.refresh()
            r, c = self.hint_move

        def on_solve(self):
            prompt = "Choose solver: 'bfs', 'dfs', 'iddfs' or 'ufc', 'astar', or 'wastar' (weighted A*)."
            algo = simpledialog.askstring('Solver', prompt, initialvalue='bfs')

            if not algo:
                return

            algo = algo.strip().lower()
            self.solver_used_in_round = True
            self.hint_move = None

            if algo == 'bfs':
                solution = bfs(self.board)

            elif algo == 'dfs':
                solution = dfs(self.board)
            elif algo == 'astar':
                solution = astar(self.board)
            elif algo in ('wastar', 'weighted', 'weighted_astar', 'weightedastar'):
                weight = simpledialog.askfloat('Weighted A*', 'Weight:', initialvalue=1.5, minvalue=1.0)
                if weight is None:
                    return
                solution = weighted_astar(self.board, weight)
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

                solution = iterative_deepening(self.board, max_depth)

            elif algo == 'ufc':
                solution = ufc(self.board)
            else:
                messagebox.showerror('Solver', "Unknown solver: use 'bfs', 'dfs', 'iddfs', 'ufc', 'astar' or 'wastar'")
                return
            if solution is None:
                messagebox.showinfo('Solve', 'There is no solution')
                return

            apply_now = messagebox.askyesno(
                'Apply solution',
                f'Solution found with {len(solution)} moves. Apply with animation?'
            )

            if apply_now:
                self.animate_solution(solution)
            else:
                messagebox.showinfo('Solution', f'Moves: {solution}')

        def animate_solution(self, solution, delay=400):
            # animate applying each toggle in sequence using after
            if not solution:
                messagebox.showinfo('Solve', 'Done. Board solved?' )
                self.finish_round_if_solved()
                return

            move = solution[0]
            self.board = self.board.toggle(move[0], move[1])
            self.refresh()

            # schedule next
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
        # if tkinter is missing, run cli
        try:
            import main as textual_main
            if hasattr(textual_main, 'main'):
                textual_main.main()
        except Exception:
            print('Could not invoke textual main.')
