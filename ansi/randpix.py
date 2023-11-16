#!/usr/bin/env python3

from sys import stdout, stdin
from time import sleep
from threading import Thread

class fg:
  black = "\u001b[30m"
  red = "\u001b[31m"
  green = "\u001b[32m"
  yellow = "\u001b[33m"
  blue = "\u001b[34m"
  magenta = "\u001b[35m"
  cyan = "\u001b[36m"
  white = "\u001b[37m"

  def rgb(r, g, b): return f"\u001b[38;2;{r};{g};{b}m"

class bg:
  black = "\u001b[40m"
  red = "\u001b[41m"
  green = "\u001b[42m"
  yellow = "\u001b[43m"
  blue = "\u001b[44m"
  magenta = "\u001b[45m"
  cyan = "\u001b[46m"
  white = "\u001b[47m"

  def rgb(r, g, b): return f"\u001b[48;2;{r};{g};{b}m"

class util:
  # attributes
  reset = "\u001b[0m"
  bold = "\u001b[1m"
  underline = "\u001b[4m"
  blink = "\u001b[5m"
  reverse = "\u001b[7m"

  # clear functions
  clear = "\u001b[2J"
  clearline = "\u001b[2K"

  # cursor attributes
  cursor_disable = "\u001b[?25l"
  cursor_enable = "\u001b[?25h"
  wrap_disable = "\u001b[?7l"
  wrap_enable = "\u001b[?7h"

  # cursor movments
  up = "\u001b[1A"
  down = "\u001b[1B"
  right = "\u001b[1C"
  left = "\u001b[1D"
  nextline = "\u001b[1E"
  prevline = "\u001b[1F"
  top = "\u001b[0;0H"

  # sixel begin/end
  #sixel_begin = "\u001bPq"
  #sixel_end = "\u001b\\"

  def init():
    stdout.write(util.reset+util.clear+util.top+util.cursor_disable+util.wrap_disable+fg.white)
    stdout.flush()

  def end():
    stdout.write(util.reset+util.clear+util.top+util.cursor_enable+util.wrap_enable)
    stdout.flush()

  def to(x, y):
    stdout.write(f"\u001b[{y};{x}H")

  def set_pixel(x, y, rgb):
    r, g, b = rgb  # r,g,b each range 0 to 255
    util.to(x, y)
    stdout.write(bg.rgb(r,g,b)+' ')

  #def set_sixel(x, y, rgb, ch):
    #r, g, b = rgb  # r,g,b each range 0 to 100
    #util.to(x, y)
    #stdout.write(util.reset+util.sixel_begin+f"#0;2;{r};{g};{b}#0{ch}"+util.sixel_end)

  def set_blink(x, y, rgb=(0, 0, 0)):
    util.to(x, y)
    r, g, b = rgb  # r,g,b each range 0 to 255
    stdout.write(bg.rgb(r, g, b)+util.blink+'@')
    stdout.flush()

  def unset_blink(x, y, rgb=(0, 0, 0)):
    util.to(x, y)
    r, g, b = rgb  # r,g,b each range 0 to 255
    stdout.write(bg.rgb(r, g, b)+' ')
    stdout.flush()


if __name__ == '__main__':

  util.init()

  for i in range(0,7):
    util.set_pixel(i, i, (255,0,0))

  for i in range(12,20):
    util.set_pixel(i, i, (0, 0, 255))

  stdout.flush()
  sleep(1)

  for i in range(0,5):
    util.set_blink(i, i, (0, 255, 0))

  sleep(5)

  for i in range(0,5):
    util.unset_blink(i , i, (255, 0, 0))

  sleep(3)

  util.end()
