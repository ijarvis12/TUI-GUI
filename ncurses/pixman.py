#!/usr/bin/env python3

import curses
import curses.panel


class DisplayServer():

  def __init__(self):
    self.screen = curses.initscr()
    # no visible cursor
    curses.curs_set(0)
    # no input echoing
    curses.noecho()
    # init color
    curses.start_color()
    # init r,g,b colors
    color_num = 0 # ranges from 0 to 216 (>256)
    color_range_step = 1000 // 5
    # r,g,b each range 0 to 1000 in curses module
    for b in range(0, 1001, color_range_step):
      for g in range(0, 1001, color_range_step):
        for r in range(0, 1001, color_range_step):
          curses.init_color(color_num, r, g, b)
          color_num += 1
    # init color pairs (use black background)
    for color in range(0, color_num):
      curses.init_pair(color, color, 0)
    # init pixel buffers
    maxy, maxx = self.screen.getmaxyx()
    self.pixel_buffers = [PixelBuffer(maxy, maxx)]
    #self.pixel_buffers[0].buffer.replace(self.screen)
    curses.panel.update_panels()
    curses.doupdate()

  def end(self):
    self.clear_screen(remove_all_buffers=True)
    curses.use_default_colors()
    curses.curs_set(2)
    curses.echo()
    curses.nocbreak()
    curses.endwin()

  def pause(self):
    self.screen.refresh()
    self.screen.getch()

  def clear_screen(self, remove_all_buffers=False):
    for pb in self.pixel_buffers:
      pb.clear(delete=remove_all_buffers)
    if remove_all_buffers:
      self.pixel_buffers = []

  def new_pixel_buffer(self, nlines=1, ncols=1, begin_y=0, begin_x=0):
    pixel_buffer = PixelBuffer(nlines, ncols, begin_y, begin_x)
    self.pixel_buffers.append(pixel_buffer)
    return pixel_buffer



class PixelBuffer():
  """Buffer of pixels that can be shown and hidden, plus moved around"""

  def __init__(self, nlines=1, ncols=1, begin_y=0, begin_x=0):
    self.buffer = curses.panel.new_panel(curses.newwin(nlines, ncols, begin_y, begin_x))
    self.buffer.top()
    self.buffer.show()
    curses.panel.update_panels()
    curses.doupdate()

  def clear(self, delete=False):
    self.buffer.window().clear()
    if delete:
      self.buffer = None
      del self

  def set_pixel(self, y=0, x=0, rgb=(0,0,0), set_blink=False):
    # y, x relative to upper left corner of buffer
    # Test if coordinates are right
    if not self.buffer.window().enclose(y, x):
      return
    # rgb - arithmetic, each range from 0 to 6
    r, g, b = rgb
    color_num = b
    color_num += 6*g
    color_num += 36*r
    cp = color_num
    # maybe set blink
    if_set_blink = curses.A_BLINK if set_blink else 0x0
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
    # y, x are relative to upper left corner of buffer
    char_and_attr = self.buffer.window().inch(y, x)
    is_blinking = (char_and_attr & curses.A_ATTRIBUTES) == curses.A_BLINK
    color_pair = char_and_attr & curses.A_COLOR
    fg_color, _ = curses.pair_content(color_pair)
    rgb = curses.color_content(fg_color) # rgb is a 3-tuple ranging from 0 to 1000
    r, g, b = rgb
    r *= 6
    g *= 6
    b *= 6
    r //= 1000
    g //= 1000
    b //= 1000
    return (is_blinking, (r, g, b))




if __name__ == '__main__':

  import random

  ds = DisplayServer()

  pb0 = ds.pixel_buffers[0]

  # try to add a sixel
  pb0.set_sixel(2, 10, rgb=(1,1,1), repeat=5, ch='~')

  ds.pause()

  for i in range(1,10):
    pb0.set_pixel(i, i, (2,0,0))

  ds.pause()

  for i in range(10,20):
    pb0.set_pixel(i, i, (5,5,5))

  ds.pause()

  for i in range(1,20):
    pb0.set_pixel(i, i, (5,0,0), True)

  ds.pause()

  for i in range(1,10):
    pb0.set_pixel(i, i, (5,0,0))

  ds.pause()

  random.seed()

  for i in range(0,16):
    for j in range(0,16):
      r = random.randrange(7)
      g = random.randrange(7)
      b = random.randrange(7)
      blnk = random.choice([True,False,False,False,False,False,False,False,False,False])
      pb0.set_pixel(i, j, (r,g,b), blnk)

  ds.pause()

  pbmaxy, pbmaxx = pb0.buffer.window().getmaxyx()

  for i in range(0,pbmaxy-1):
    for j in range(0,pbmaxx-1):
      pb0.set_pixel(i, j, (5,5,5))

  ds.pause()

  is_blink, rgb = pb0.get_pixel(5,5)
  pb0.buffer.window().addstr(7,7, str(rgb))
  pb0.buffer.window().addstr(8,8, str(is_blink))

  ds.pause()

  for j in range(0, pbmaxx):
    pb0.buffer.window().vline(0, j, '@', pbmaxy)

  ds.pause()

  ds.clear_screen(remove_all_buffers=False)

  ds.pause()


  ds.end()
