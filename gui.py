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


if TK_AVAILABLE:
    class LightsOutGUI:
        def __init__(self, master, start_board: Board = None):
            self.master = master
            self.board_size = Board.board_size
            self.start_board = start_board or Board([[0]*self.board_size for _ in range(self.board_size)])
            self.board = self.start_board

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

            tk.Button(ctrl, text='Randomize', command=self.on_random).grid(row=0, column=0, padx=4)
            tk.Button(ctrl, text='Solve', command=self.on_solve).grid(row=0, column=1, padx=4)
            tk.Button(ctrl, text='Reset', command=self.on_reset).grid(row=0, column=2, padx=4)
            tk.Button(ctrl, text='Quit', command=master.quit).grid(row=0, column=3, padx=4)

            self.status = tk.Label(master, text='')
            self.status.pack(pady=(4,0))

            self.refresh()

        def color_for(self, val: int) -> str:
            return '#ffd54f' if val else '#9e9e9e'

        def refresh(self):
            for r in range(self.board_size):
                for c in range(self.board_size):
                    val = self.board.grid[r][c]
                    b = self.buttons[r][c]
                    b.config(bg=self.color_for(val), activebackground=self.color_for(val))
            self.status.config(text='Solved' if self.board.is_goal() else 'Not solved')

        def on_press(self, r: int, c: int):
            # Board.toggle returns a new Board
            self.board = self.board.toggle(r, c)
            self.refresh()

        def on_random(self):
            moves = simpledialog.askinteger('Randomize', 'Number of random presses:', initialvalue=8, minvalue=1, maxvalue=100)
            if moves is None:
                return
            self.board = self.start_board
            for _ in range(moves):
                r = random.randrange(self.board_size)
                c = random.randrange(self.board_size)
                self.board = self.board.toggle(r, c)
            self.refresh()

        def on_reset(self):
            self.board = self.start_board
            self.refresh()

        def on_solve(self):
            algo = simpledialog.askstring('Solver', "Choose solver: 'bfs' or 'dfs'", initialvalue='bfs')
            if not algo:
                return
            algo = algo.strip().lower()
            if algo == 'bfs':
                solution = bfs(self.board)
            elif algo == 'dfs':
                solution = dfs(self.board)
            else:
                messagebox.showerror('Solver', 'Unknown solver: use bfs or dfs')
                return

            if solution is None:
                messagebox.showinfo('Solve', 'There is no solution')
                return

            apply_now = messagebox.askyesno('Apply solution', f'Solution found with {len(solution)} moves. Apply with animation?')
            if apply_now:
                self.animate_solution(solution)
            else:
                messagebox.showinfo('Solution', f'Moves: {solution}')

        def animate_solution(self, solution, delay=400):
            # animate applying each toggle in sequence using after
            if not solution:
                messagebox.showinfo('Solve', 'Done. Board solved?' )
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
