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
        maxy0, maxx0 = screen.getmaxyx()
        new_y_len = int((maxy0-2)/(len(windows)+1))
        # loop through windows, resize, move, add hline
        for idx,w in enumerate(windows):
               w.resize(new_y_len, maxx0)
               w.mvwin(new_y_len*idx, 0)
               screen.hline(new_y_len*(idx+1), 0, '#', maxx0)
               w.refresh()
        # create new window
        win = screen.subwin(new_y_len, maxx0, len(windows)*new_y_len+1, 0)
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        windows.append(win)
        screen.refresh()
        # return textbox for editing
        return Textbox(win)

def create_screen(screen_num, screens, panels, cmdlines, cmds, windows):
        # setup screen
        screens[screen_num] = curses.initscr()
        panels[screen_num] = new_panel(screens[screen_num])
        panels[screen_num].top()
        update_panels()
        curses.doupdate()
        maxy, maxx = screens[screen_num].getmaxyx()

        # setup cmdline
        cmdlines[screen_num] = screens[screen_num].subwin(1, maxx, maxy-1, 0)
        cmdlines[screen_num].idcok(True)
        cmds[screen_num] = Textbox(cmdlines[screen_num])
        cmds[screen_num].stripspaces = True

        # setup window
        win = screens[screen_num].subwin(maxy-2, maxx, 0, 0)
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        if screen_num in windows:
                windows[screen_num].append(win)
        else:
                windows[screen_num] = [win]

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
        del text_boxes[screen_num][-1]
        del windows[-1]
        # get useful properties
        len_win = len(windows)
        if len_win > 1:
                maxy0, maxx0 = screen.getmaxyx()
                new_y_len = int((maxy0-2)/len_win)
        else:
                maxy0, maxx0 = screen.getmaxyx()
                new_y_len = maxy0-2
        # loop through windows, moving, resizing, adding hlines
        for idx,w in enumerate(windows):
                if idx > 0:
                        w.mvwin(new_y_len*idx+1, 0)
                        screen.hline(new_y_len*idx, 0, '#', maxx0)
                w.resize(new_y_len, maxx0)
                w.refresh()
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

        screen_num = 0
        win_num = 0

        # inital text box
        text_boxes[screen_num] = [create_screen(screen_num, screens, panels, cmdlines, cmds, windows)]
        text_boxes[screen_num][win_num].edit() # Ctrl-g to exit the text_box


        # run the program
        cmds[screen_num].edit()
        c = cmds[screen_num].gather()
        while c != '':
                # new screen
                if c == 'n ':
                        screen_num = len(screens)
                        text_boxes[screen_num] = [create_screen(screen_num, screens, panels, cmdlines, cmds, windows)]
                        win_num = 0
                        text_boxes[screen_num][win_num].edit()
                elif c == 'nw ':
                        if len(windows[screen_num]) < 4:
                                win_num = len(windows[screen_num])
                                text_boxes[screen_num].append(split_win(screen_num, screens, windows))
                                text_boxes[screen_num][win_num].edit()
                # remove screen
                elif c == 'r ':
                        if len(screens) > 1:
                                screen_num = remove_screen(screen_num, screens, panels, cmdlines, cmds, windows, text_boxes)
                                win_num = 0
                        text_boxes[screen_num][win_num].edit()
                elif c == 'rw ':
                        if len(windows[screen_num]) > 1:
                                remove_win(screen_num, screens, windows, text_boxes)
                                win_num = 0
                        text_boxes[screen_num][win_num].edit()
                # next screen
                elif c == 's ':
                        if screen_num < len(screens) - 1:
                                screen_num += 1
                                win_num = 0
                        else:
                                screen_num = 0
                                win_num = 0
                        panels[screen_num].top()
                        update_panels()
                        curses.doupdate()
                        text_boxes[screen_num][win_num].edit()
                # next window
                elif c == 'w ':
                        if win_num < len(windows[screen_num]) - 1:
                                win_num += 1
                        else:
                                win_num = 0
                        text_boxes[screen_num][win_num].edit()
                # get cmd
                cmdlines[screen_num].clear()
                cmds[screen_num].edit()
                c = cmds[screen_num].gather()

        # end program
        curses.endwin()
        return


if __name__ == '__main__':
        wrapper(main)
