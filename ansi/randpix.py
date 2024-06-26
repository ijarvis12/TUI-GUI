#!/usr/bin/env python3

from sys import stdout
from time import sleep

write = stdout.write
flush = stdout.flush

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

  # cursor movements
  up = "\u001b[1A"
  down = "\u001b[1B"
  right = "\u001b[1C"
  left = "\u001b[1D"
  nextline = "\u001b[1E"
  prevline = "\u001b[1F"
  top = "\u001b[0;0H"

  # sixel begin/end
  sixel_begin = "\033Pq"
  sixel_end = "\033\\"

  def init():
    write(util.reset+util.clear+util.top+util.cursor_disable+util.wrap_disable)
    flush()

  def end():
    write(util.reset+util.clear+util.top+util.cursor_enable+util.wrap_enable)
    flush()

  def to(x, y):
    write(f"\u001b[{y};{x}H")

  def pause():
    flush()
    _ = input(util.reset+fg.white)

  def set_pixel(x, y, rgb=(255, 255, 255), blink=False):
    r, g, b = rgb  # r,g,b each range 0 to 255
    util.to(x, y)
    if_blnk = util.blink if blink else util.reset
    write(if_blnk+fg.rgb(r,g,b)+'@')

  def set_sixel(x, y, rgb=(0, 0, 0), repeat=12, ch='~'):
    r, g, b = rgb  # r,g,b each range 0 to 100
    util.to(x, y)
    write(util.sixel_begin+f"#0;2;{r};{g};{b}#0!{repeat}{ch}"+util.sixel_end)


if __name__ == '__main__':

  util.init()

  # grey scale
  stop = 384
  for i in range(stop+1):
    util.set_sixel(1,1,(100*i//stop,100*i//stop,100*i//stop),stop-i)

  # pretty color triangle
  for y in range(101):
    for x in range(y+1):
      util.set_sixel(x, y, (y-x, x, 100-y), 6)

  # a faster one
  for y in range(101):
    util.to(0, y)
    write(util.sixel_begin)
    for x in range(y+1):
      write(f"#{x};2;{y-x};{x};{100-y}#{x}!3~")
    write("-")
    write(util.sixel_end)

  util.pause()

  for i in range(0,7):
    util.set_pixel(i, i, (255,0,0))

  for i in range(12,20):
    util.set_pixel(i, i, (0, 0, 255))

  util.pause()

  for i in range(0,5):
    util.set_pixel(i, i, (0, 255, 0), True)

  util.pause()

  for i in range(0,5):
    util.set_pixel(i , i, (255, 0, 0))

  util.pause()

  import random

  random.seed()

  for i in range(0,20):
    for j in range(0,50):
      r = random.randrange(256)
      g = random.randrange(256)
      b = random.randrange(256)
      blnk = random.choice([True,False,False,False])
      util.set_pixel(j, i, (r, g, b), blnk)

  util.pause()

  util.end()
