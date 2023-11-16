#!/usr/bin/env python3

import curses
from cusser import Cusser

class DisplayServer():

        def __init__(self, stdscr):
                self.screen = stdscr = Cusser(stdscr)
                curses.curs_set(0)
                curses.noecho()

        def __del__(self):
                curses.endwin()

        def end(self):
                self.__del__()

        def set_pixel(self, y, x, rgb=(0, 0, 0), blink=False):
                r, g, b = rgb                           # r,g,b each range 0 to 255
                #string = f"\033[{y};{x}H"              # position
                self.screen.move(y, x)
                string = "\033[5m" if blink else ""     # blink
                string += f"\033[38;2;{r};{g};{b}m"     # color
                string += '@'                           # pixel
                self.screen.addstr(string)

        def pause(self):
                self.screen.getch()


def main(stdscr):

        ds = DisplayServer(stdscr)

        ds.screen.addstr(str(curses.COLOR_PAIRS))

        # trying to add a sixel
        #ds.screen.addstr("\033Pq#0;2;100;0;0#0~\033\\")
        #ds.screen.refresh()

        # add ansi background color
        #ds.screen.addstr("\033[42m ")
        #ds.screen.refresh()

        ds.pause()

        for i in range(1,10):
                ds.set_pixel(i, i, (0, 0, 0), False)

        ds.pause()

        for i in range(10,20):
                ds.set_pixel(i, i, (255, 0, 0), False)

        ds.pause()

        for i in range(1,20):
                ds.set_pixel(i, i, (0, 0, 255), True)

        ds.pause()

        ds.end()



if __name__ == '__main__':
        curses.wrapper(main)
