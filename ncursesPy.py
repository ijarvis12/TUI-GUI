#!/usr/bin/env python3

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle
from curses.panel import *

def main(stdscr):
        stdscr.clear()
        begin_x = 20; begin_y = 7
        height = 25; width = 80
        win = curses.newwin(height, width, begin_y, begin_x)
        stdscr.refresh()

        rectangle(stdscr, begin_y-1, begin_x-1, begin_y+height, begin_x+width)
        stdscr.refresh()

        pane = new_panel(win)

        box = Textbox(win)
        box.edit()

        return


if __name__ == '__main__':
        wrapper(main)
