#!/usr/bin/env python3

import curses
from curses import wrapper, window
from curses.textpad import Textbox
from curses.panel import *

def split_win(screen_num, screens, windows):
        # clear screen of hlines
        screen = screens[screen_num]
        screen.clear()
        # window to create
        win = None
        # get useful properties
        windows = windows[screen_num]
        len_win = len(windows)
        maxy0, maxx0 = screen.getmaxyx()
        new_y_len = round((maxy0-2)/(len_win+1))
        # loop through windows, resize, move, add hline
        for idx,wins in windows.items():
               for w in wins:
                       maxy, maxx = w.getmaxyx()
                       y, x = w.getparyx()
                       w.resize(new_y_len, maxx)
                       w.mvwin(new_y_len*idx+idx, x)
                       w.refresh()
               screen.hline(new_y_len*(idx+1)+idx, 0, '#', maxx0)
        # create new window
        if len(windows) > 1:
                new_y_len_bool = True
        else:
                new_y_len_bool = False
        win = screen.subwin(new_y_len-new_y_len_bool, maxx0, len_win*new_y_len+len_win, 0)
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        windows[len_win] = [win]
        # bottom hline
        if len(windows) < 3:
                screen.hline(maxy0-2, 0, '#', maxx0)
        screen.refresh()
        # return textbox for editing
        return Textbox(win)

def create_screen(screen_num, screens, panels, cmdlines, cmds, windows):
        # setup screen
        screens[screen_num] = curses.initscr()
        screen = screens[screen_num]
        panels[screen_num] = new_panel(screen)
        panels[screen_num].top()
        update_panels()
        curses.doupdate()
        maxy, maxx = screen.getmaxyx()

        # setup cmdline
        cmdlines[screen_num] = screen.subwin(1, maxx, maxy-1, 0)
        cmdlines[screen_num].idcok(True)
        cmds[screen_num] = Textbox(cmdlines[screen_num])
        cmds[screen_num].stripspaces = True

        # setup window
        win = screen.subwin(maxy-2, maxx, 0, 0)
        screen.hline(maxy-2, 0, '#', maxx)
        screen.refresh()
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        windows[screen_num] = {0:[win]}

        # return text box for text_boxes, and immediate editing
        return Textbox(win)

def remove_screen(screen_num, screens, panels, cmdlines, cmds, windows, text_boxes):
        # remove screen and associated objects
        del text_boxes[screen_num]
        del windows[screen_num]
        del cmds[screen_num]
        del cmdlines[screen_num]
        del panels[screen_num]
        del screens[screen_num]
        # get new screen number
        screen_num = len(screens)-1
        # put screen on top
        panels[screen_num].top()
        update_panels()
        curses.doupdate()
        # return screen number
        return screen_num


def remove_win(screen_num, screens, windows, text_boxes):
        # clear screen of hlines
        screen = screens[screen_num]
        screen.clear()
        # get windows object list
        windows = windows[screen_num]
        # remove last window
        del text_boxes[screen_num][len(windows)-1]
        del windows[len(windows)-1]
        # get useful properties
        len_win = len(windows)
        maxy0, maxx0 = screen.getmaxyx()
        if len_win > 1:
                new_y_len = round((maxy0-2)/len_win)
        else:
                new_y_len = maxy0-2
        # loop through windows, moving, resizing, adding hlines
        # somewhat of a hack using idx for precise placement
        for idx,wins in windows.items():
                for w in wins:
                        y, x = w.getparyx()
                        maxy, maxx = w.getmaxyx()
                        if idx > 0:
                                w.mvwin(new_y_len*idx+idx, x)
                        if idx == 2:
                                w.resize(new_y_len-1, maxx)
                        else:
                                w.resize(new_y_len, maxx)
                        w.refresh()
                if idx < len(windows) - 1:
                        screen.hline(new_y_len*(idx+1)+idx, 0, '#', maxx0)
        if len(windows) < 3:
                screen.hline(maxy0-2, 0, '#', maxx0)
        # update screen
        screen.refresh()
        # return nothing
        return

def main(stdscr):
        # screen setup
        stdscr.clear()
        screens = {}
        panels = {}
        cmdlines = {}
        cmds = {}
        windows = {}
        text_boxes = {}

        # index vars
        screen_num = 0
        win_num = [0, 0]

        # inital text box
        text_boxes[screen_num] = {0:[create_screen(screen_num, screens, panels, cmdlines, cmds, windows)]}
        text_boxes[screen_num][win_num[0]][win_num[1]].edit() # Ctrl-g to exit the text_box


        # run the program
        cmds[screen_num].edit()
        c = cmds[screen_num].gather()
        while c != '':
                # new screen
                if c == 'n ':
                        screen_num = len(screens)
                        text_boxes[screen_num] = {0:[create_screen(screen_num, screens, panels, cmdlines, cmds, windows)]}
                        win_num = [0, 0]
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                elif c == 'nw ':
                        if len(windows[screen_num]) < 4:
                                win_num = [len(windows[screen_num]), 0]
                                text_boxes[screen_num][win_num[0]] = [split_win(screen_num, screens, windows)]
                                text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                # remove screen
                elif c == 'r ':
                        if len(screens) > 1:
                                screen_num = remove_screen(screen_num, screens, panels, cmdlines, cmds, windows, text_boxes)
                                win_num = [0, 0]
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                elif c == 'rw ':
                        if len(windows[screen_num]) > 1:
                                remove_win(screen_num, screens, windows, text_boxes)
                                win_num = [0, 0]
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                # next screen
                elif c == 's ':
                        if screen_num < len(screens) - 1:
                                screen_num += 1
                        else:
                                screen_num = 0
                        win_num = [0, 0]
                        panels[screen_num].top()
                        update_panels()
                        curses.doupdate()
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                # next window
                elif c == 'w ':
                        if len(windows[screen_num][win_num[0]]) > 1 and win_num[1] < (len(windows[screen_num][win_num[0]]) - 1):
                                win_num = [win_num[0], win_num[1]+1]
                        elif win_num[0] < (len(windows[screen_num]) - 1):
                                win_num = [win_num[0]+1, 0]
                        else:
                                win_num = [0, 0]
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                # get cmd
                cmdlines[screen_num].clear()
                cmds[screen_num].edit()
                c = cmds[screen_num].gather()

        # end program
        curses.endwin()
        return


if __name__ == '__main__':
        wrapper(main)
