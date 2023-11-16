#!/usr/bin/env python3

import curses
import curses.ascii
from cusser import Cusser

class DisplayServer():

        def __init__(self, stdscr):
                self.screen = stdscr = Cusser(stdscr)
                #curses.noraw()
                curses.curs_set(0)
                curses.start_color()
                curses.use_default_colors()
                self.screen.attron(curses.A_BLINK)

        def __del__(self):
                curses.endwin()

        def end(self):
                self.__del__()

        def set_pixel(self, y, x, rgb, blink=False):
                r, g, b = rgb  # r,g,b each range 0 to 1000
                curses.init_color(7, r, g, b)
                curses.init_pair(1, curses.COLOR_WHITE, 7)
                ch = '.' if blink else ' '
                self.screen.addch(y, x, ch, curses.color_pair(1))

        def set_pixel_blink(self, y, x):
                ch = self.screen.inch(y, x)
                attr = ch & 0xFF00
                self.screen.addch(y, x, '.', attr)

        def unset_pixel_blink(self, y, x):
                ch = self.screen.inch(y, x)
                attr = ch & 0xFF00
                self.screen.addch(y, x, ' ', attr)

        def pause(self):
                self.screen.getch()


def main(stdscr):

        ds = DisplayServer(stdscr)

        ds.screen.addstr(str(curses.COLOR_PAIRS))

        # trying to add a sixel
        ds.screen.addstr("\033Pq#0;2;100;0;0#0~\033\\")

        for i in range(1,10):
                ds.set_pixel(i, i, (0, 0, 0), True)

        ds.pause()

        for i in range(10,20):
                ds.set_pixel(i, i, (1000, 0, 0), True)

        ds.pause()

        for i in range(1,20):
                ds.unset_pixel_blink(i, i)

        ds.pause()

        ds.end()



if __name__ == '__main__':
        curses.wrapper(main)
