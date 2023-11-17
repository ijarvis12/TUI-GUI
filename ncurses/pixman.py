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

        def set_sixel(self, y, x, rgb=(0, 0, 0), repeat=1, ch='~'):
                r, g, b = rgb                   # r,g,b each range 0 to 100
                r = int(2.5*r)
                g = int(2.5*r)
                b = int(2.5*r)
                binary = bin(ord(ch) - 63)[2:]
                y_range = []
                for e,b in enumerate(binary[::-1]):
                        y_range.append(e)
                for i in range(0,repeat):
                        for j in y_range:
                                self.set_pixel(y+j, x+i, rgb=(r, g, b))





if __name__ == '__main__':

        import random

        def main(stdscr):

                ds = DisplayServer(stdscr)

                ds.screen.addstr(str(curses.COLOR_PAIRS))

                # trying to add a sixel
                ds.set_sixel(2, 10, repeat=5, ch='~')

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

                random.seed()

                for i in range(0,15):
                        for j in range(0,15):
                                r = random.randrange(256)
                                g = random.randrange(256)
                                b = random.randrange(256)
                                blnk = random.choice([True,False,False,False])
                                ds.set_pixel(i, j, (r, g, b), blnk)

                ds.pause()

                ds.end()


        curses.wrapper(main)
