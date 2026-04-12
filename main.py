from gui import main as gui_main, TK_AVAILABLE


if __name__ == '__main__':
    start_board = None
    if TK_AVAILABLE:
        gui_main(start_board)
    else:
        print('To run the game you need to install tkinter')





