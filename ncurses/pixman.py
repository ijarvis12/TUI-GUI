#!/usr/bin/env python3

import curses
import curses.panel


class DisplayServer():
  """Because of the limitations of ncurses, we can only do 8 bit color for python3.9"""

  def __init__(self):
    self.screen = curses.initscr()
    # no visible cursor
    curses.curs_set(0)
    # no input echoing
    curses.noecho()
    # init color
    curses.start_color()
    self.max_color_num = curses.COLORS - 1
    self.max_color_pair = (curses.COLOR_PAIRS - 1) // 2  # Bug in python3.9 / ncurses 5, only goes to 32k (not 64k)
    # init black and white colors
    curses.init_color(0, 0, 0, 0)  # black
    curses.init_color(self.max_color_num, 1000, 1000, 1000)  # white
    # init r,g,b colors
    color_num = 0
    color_range_step = 3000 // int(curses.COLORS**(1/3))
    # r,g,b each range 0 to 1000
    for r in range(0, 1001, color_range_step):
      for g in range(0, 1001, color_range_step):
        for b in range(0, 1001, color_range_step):
          color_num += 1
          curses.init_color(color_num, r, g, b)
    # init color pairs (use black background)
    for color in range(1, self.max_color_num):
      curses.init_pair(color, color, 0)
    # init pair white on black
    curses.init_pair(self.max_color_num, self.max_color_num, 0)
    # clear the rest of the color pairs (for get_pixel not mixing up)
    for cp in range(self.max_color_num+1, self.max_color_pair):
      curses.init_pair(cp, 0, 0)
    # init pixel buffers
    self.pixel_buffers = []

  def end(self):
    self.clear_screen(True)
    curses.use_default_colors()
    curses.curs_set(2)
    curses.echo()
    curses.nocbreak()
    curses.endwin()

  def pause(self):
    self.screen.getch()

  def clear_screen(self, remove_all_buffers=False):
    for pb in self.pixel_buffers:
      pb.buffer.hide()
    curses.panel.update_panels()
    curses.doupdate()
    if remove_all_buffers:
      for pb in self.pixel_buffers:
        pb.clear(delete=True)
      self.pixel_buffers = []

  def new_pixel_buffer(self, nlines=1, ncols=1, begin_y=0, begin_x=0):
    pixel_buffer = PixelBuffer(self.screen, nlines, ncols, begin_y, begin_x)
    self.pixel_buffers.append(pixel_buffer)
    return pixel_buffer



class PixelBuffer():
  """Buffer of pixels that can be shown and hidden, plus moved around"""

  def __init__(self, screen_or_window, nlines=1, ncols=1, begin_y=0, begin_x=0):
    self.buffer = curses.panel.new_panel(screen_or_window)
    self.buffer.top()
    self.buffer.show()

  def clear(self, delete=False):
    self.buffer.window().clear()
    self.buffer.window().refresh()
    if delete:
      self.buffer = None
      del self

  def set_pixel(self, y=0, x=0, rgb=(0,0,0), set_blink=False):
    # y, x relative to upper left corner of buffer
    # Test if coordinates are right
    if not self.buffer.window().enclose(y, x):
      return
    # rgb - arithmetic, each range from 0 to 255
    r, g, b = rgb
    r //= 3  # if using 24 bit color comment out this line
    g //= 3  # ditto
    b //= 3  # ditto
    color_num = int(b)
    color_num += int(g+(curses.COLORS/3)) if g != 0 else 0
    color_num += int(r+(curses.COLORS*(2/3))) if r != 0 else 0
    cp = color_num
    # get pixel blinking attr
    already_blinking = (self.buffer.window().inch(y, x) & curses.A_ATTRIBUTES) == curses.A_BLINK
    # maybe set pixel blinking attr
    if already_blinking and not set_blink:
      if_set_blink = curses.A_BLINK
    elif not already_blinking and set_blink:
      if_set_blink = curses.A_BLINK
    else:
      if_set_blink = 0x0
    # set pixel
    self.buffer.window().addch(y, x, '@', curses.color_pair(cp) | if_set_blink)

  def set_sixel(self, y=0, x=0, rgb=(0,0,0), repeat=1, ch='~'):
    # get binary bitmask of sixel
    binary = bin(ord(ch) - 63)[2:]
    # get pixels to set
    y_range = []
    for e,b in enumerate(binary[::-1]):
      y_range.append(e)
    # set pixels
    for i in range(0,repeat):
      for j in y_range:
        self.set_pixel(y+j, x+i, rgb)

  def get_pixel(self, y, x):
    char_and_attr = self.buffer.window().inch(y, x)
    is_blinking = (char_and_attr & curses.A_ATTRIBUTES) == curses.A_BLINK
    color_pair = (char_and_attr & curses.A_COLOR) // 2  # Bug in Python 3.9 / ncurses 5
    fg_color, _ = curses.pair_content(color_pair)
    rgb = curses.color_content(fg_color) # rgb is a 3-tuple ranging from 0 to 1000
    r, g, b = rgb
    r *= 255
    g *= 255
    b *= 255
    r //= 1000
    g //= 1000
    b //= 1000
    return (is_blinking, (r, g, b))




if __name__ == '__main__':

  import random

  ds = DisplayServer()

  maxy, maxx = ds.screen.getmaxyx()

  pb0 = ds.new_pixel_buffer(maxy-1, maxx-1)

  # try to add a sixel
  pb0.set_sixel(2, 10, rgb=(100,100,100), repeat=5, ch='~')

  ds.pause()

  for i in range(1,10):
    pb0.set_pixel(i, i, (200,0,0))

  ds.pause()

  for i in range(10,20):
    pb0.set_pixel(i, i, (16,16,16))

  ds.pause()

  for i in range(1,20):
    pb0.set_pixel(i, i, (255,0,0), True)

  ds.pause()

  for i in range(1,10):
    pb0.set_pixel(i, i, (255,0,0))

  ds.pause()

  random.seed()

  for i in range(0,16):
    for j in range(0,16):
      r = random.randrange(256)
      g = random.randrange(256)
      b = random.randrange(256)
      blnk = random.choice([True,False,False,False,False,False,False,False,False,False])
      pb0.set_pixel(i, j, (r,g,b), blnk)

  ds.pause()

  pbmaxy, pbmaxx = pb0.buffer.window().getmaxyx()

  for i in range(0,pbmaxy-1):
    for j in range(0,pbmaxx-1):
      pb0.set_pixel(i, j, (255,255,255))

  ds.pause()

  is_blink, rgb = pb0.get_pixel(5,5)
  pb0.buffer.window().addstr(7,7, str(rgb))
  pb0.buffer.window().addstr(8,8, str(is_blink))

  ds.pause()

  ds.clear_screen(remove_all_buffers=True)

  ds.pause()

  ds.end()

  #curses.endwin()
