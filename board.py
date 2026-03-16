class Board:
    board_size = 4

    def __init__(self, grid):
        self.grid = grid

    def toggle(self, x, y):
        new_grid = [row[:] for row in self.grid] # making a copy so original one is not modified

        for dx, dy in [(0,0), (1,0), (-1,0), (0,1), (0,-1)]:
            new_x = x + dx
            new_y = y + dy

            if 0 <= new_x < self.board_size and 0 <= new_y < self.board_size:
                new_grid[new_x][new_y] ^= 1 # ^= changes 1 -> 0 and 0 -> 1

        return Board(new_grid)

    def is_goal(self):
        for row in self.grid:
            if 1 in row:
                return False
        return True

    def display(self):
        for row in self.grid:
            print(" ".join(str(cell) for cell in row))
        print()

