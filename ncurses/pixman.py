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

        def pause(self):
                self.screen.getch()

        def set_pixel(self, y, x, rgb=(0, 0, 0), blink=False):
                r, g, b = rgb                                   # r,g,b each range 0 to 255
                string = ""
                #string += f"\033[{y};{x}H"                     # position (slower)
                self.screen.move(y, x)                          # position
                string += "\033[5m" if blink else "\033[0m"     # blink
                string += f"\033[38;2;{r};{g};{b}m"+'@'         # color and pixel char
                self.screen.addstr(string)

        def set_sixel(self, y, x, rgb=(0, 0, 0), repeat=12, ch='~'):
                r, g, b = rgb                   # r,g,b each range 0 to 100
                self.screen.move(y, x)
                string = "\033Pq"               # start sixel
                string += f"#0;2;{r};{g};{b}"   # color
                string += f"#0!{repeat}{ch}"    # pixels to repeat
                string += "\033\\"              # end sixel
                self.screen.addstr(string)


def main(stdscr):

        ds = DisplayServer(stdscr)

        ds.screen.addstr(str(curses.COLOR_PAIRS))

        # trying to add a sixel
        ds.set_sixel(2, 3)

        ds.pause()

        for i in range(1,10):
                ds.set_pixel(i, i, (0, 0, 0))

        ds.pause()

        for i in range(10,20):
                ds.set_pixel(i, i, (255, 0, 0))

        ds.pause()

        for i in range(1,20):
                ds.set_pixel(i, i, (0, 0, 255), True)

        ds.pause()

        for i in range(1,10):
                ds.set_pixel(i, i, (0, 0, 255))

        ds.pause()

        ds.end()



if __name__ == '__main__':
        curses.wrapper(main)
