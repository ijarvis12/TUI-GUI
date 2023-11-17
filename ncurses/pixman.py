#!/usr/bin/env python3

import curses


class DisplayServer():
  """Because of the limitations of ncurses, we can only do 8 bit color"""

  def __init__(self, stdscr):
    self.screen = stdscr
    curses.curs_set(0)
    curses.noecho()
    # init colors
    curses.start_color()
    # init black and white colors
    curses.init_color(0, 0, 0, 0)
    curses.init_color(curses.COLORS-1, 1000, 1000, 1000)
    # init white background
    curses.init_pair(curses.COLORS-1, 0, curses.COLORS-1)
    self.screen.bkgd(' ', curses.color_pair(curses.COLORS-1))
    color_num = 0
    color_range_step = 3000 // int(curses.COLORS**(1/3))
    # r,g,b each range 0 to 1000
    for r in range(0, 1001, color_range_step):
      for g in range(0, 1001, color_range_step):
        for b in range(0, 1001, color_range_step):
          color_num += 1
          curses.init_color(color_num, r, g, b)
    for cp in range(1, curses.COLORS-1):
      curses.init_pair(cp, cp, curses.COLORS-1)

  def __del__(self):
    curses.endwin()

  def end(self):
    self.__del__()

  def pause(self):
    self.screen.getch()

  def set_pixel(self, y, x, cp=0, set_blink=False):
    # get pixel blinking attr
    already_blinking = (self.screen.inch(y, x) & curses.A_ATTRIBUTES) == curses.A_BLINK
    # maybe set pixel blinking attr
    if already_blinking and not set_blink:
      if_set_blink = curses.A_BLINK
    elif not already_blinking and set_blink:
      if_set_blink = curses.A_BLINK
    else:
      if_set_blink = 0
    # set pixel
    self.screen.addch(y, x, '@', curses.color_pair(cp) | if_set_blink)

  def set_sixel(self, y, x, cp=0, repeat=1, ch='~'):
    binary = bin(ord(ch) - 63)[2:]
    y_range = []
    for e,b in enumerate(binary[::-1]):
      y_range.append(e)
    for i in range(0,repeat):
      for j in y_range:
        self.set_pixel(y+j, x+i, cp)





if __name__ == '__main__':

  import random

  def main(stdscr):

    ds = DisplayServer(stdscr)

    ds.screen.addstr(str(curses.COLOR_PAIRS)+' '+str(curses.COLORS))

    # trying to add a sixel
    ds.set_sixel(2, 10, repeat=5, ch='~')

    ds.pause()

    for i in range(1,10):
      ds.set_pixel(i, i, 0)

    ds.pause()

    for i in range(10,20):
      ds.set_pixel(i, i, 16)

    ds.pause()

    for i in range(1,20):
      ds.set_pixel(i, i, 255, True)

    ds.pause()

    for i in range(1,10):
      ds.set_pixel(i, i, 255)

    ds.pause()

    random.seed()

    for i in range(0,15):
      for j in range(0,15):
        cp = random.randrange(0, curses.COLORS-1)
        blnk = random.choice([True,False,False,False])
        ds.set_pixel(i, j, cp, blnk)

    ds.pause()

    maxy, maxx = ds.screen.getmaxyx()

    for i in range(0,maxy-1):
      for j in range(0,maxx-1):
        ds.set_pixel(i, j)

    ds.pause()

    ds.end()


  curses.wrapper(main)
