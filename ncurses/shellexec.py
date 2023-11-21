#!/usr/bin/env python3

import curses
import curses.ascii
import os
import sys
import socket


executables = os.listdir('/usr/sbin')
for cmd in os.listdir('/usr/bin'):
  executables.append(cmd)
for cmd in os.listdir('/usr/local/sbin'):
  executables.append(cmd)
for cmd in os.listdir('/usr/local/bin'):
  executables.append(cmd)



def main(stdscr):

  prepend = os.getlogin()+'@'+socket.gethostname()+'$ '
  stdscr.addstr(0,0,prepend)
  start_cmd_pos = len(prepend)

  chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-=_+[]\\{}|;\':\",./<>? "

  x = 0
  cmd = ""
  char = stdscr.getch()
  while char != curses.ascii.NL:
    if chr(char) not in chars and len(cmd) > 0:
      x -= 1
      cmd = cmd[:-1]
      update_cmd_display(stdscr, cmd)
      stdscr.move(0,len(prepend))
      stdscr.addstr(cmd+' ')
      stdscr.move(0,len(prepend)+x)
    elif chr(char) not in chars:
      pass
    else:
      cmd += chr(char)
      x += 1
      update_cmd_display(stdscr, cmd)
      stdscr.move(0,len(prepend))
      stdscr.addstr(cmd)
    char = stdscr.getch()
  return cmd


def update_cmd_display(stdscr, cmd):
  cmds = []
  # get possible commands
  for command in executables:
    if cmd in command:
      cmds.append(command)
  # clear cmd display before displaying new commands
  for y_pos in range(2,stdscr.getmaxyx()[0]):
    stdscr.hline(y_pos,0,' ',stdscr.getmaxyx()[1]-1)
  # display commands
  if len(cmds) > 0:
    y = 1
    x = 0
    c = 0
    brk = False
    while y < (stdscr.getmaxyx()[0] - 1):
      if brk or c > (len(cmds) - 1):
        break
      y += 1
      x = 0
      while x < (stdscr.getmaxyx()[1] - len(cmds[c]) - 1):
        stdscr.addstr(y, x, cmds[c])
        x += len(cmds[c])+1
        c += 1
        if c > (len(cmds) - 1):
          brk = True
          break



if __name__ == '__main__':
  cmd = curses.wrapper(main)
  os.system(cmd)
