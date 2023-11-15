#!/usr/bin/env python3

import curses
import curses.ascii

class DisplayServer():

        def __init__(self):
                self.screen = curses.initscr()
                curses.curs_set(0)
                curses.start_color()
                curses.use_default_colors()
                self.screen.attron(curses.A_BLINK)
                self.buffer = []
                for i in range(0,20):
                        self.buffer.append([])
                        for j in range(0,20):
                                self.buffer[i].append([0,0,0])

        def __del__(self):
                self.buffer = []
                curses.endwin()

        def end(self):
                self.__del__()

        def set_pixel(self, y, x, rgb):
                r, g, b = rgb
                curses.init_color(7, r, g, b)
                curses.init_pair(1, 7, 0)
                self.buffer[y][x] = [r,g,b]
                self.screen.addch(y, x, ' ', curses.color_pair(1)) # note how this unsets blink

        def set_pixel_blink(self, y, x):
                r,g,b = self.buffer[y][x]
                curses.init_color(7,r,g,b)
                curses.init_pair(1,7,0)
                self.screen.addch(y, x, '.', curses.color_pair(1))

        def unset_pixel_blink(self, y, x):
                r,g,b = self.buffer[y][x]
                curses.init_color(7,r,g,b)
                curses.init_pair(1,7,0)
                self.screen.addch(y, x, ' ', curses.color_pair(1))


        def pause(self):
                self.screen.getch()


def main(stdscr):
        ds = DisplayServer()

        ds.screen.addstr(str(curses.COLOR_PAIRS))

        for i in range(1,20):
                ds.set_pixel(i, i, (1000, 1000, 1000))
                ds.set_pixel_blink(i , i)

        ds.pause()

        for i in range(0,20):
                ds.unset_pixel_blink(i, i)

        ds.pause()

        ds.end()


if __name__ == '__main__':
        curses.wrapper(main)
