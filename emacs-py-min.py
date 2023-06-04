#!/usr/bin/env python3

import curses
from curses import wrapper, window
from curses.textpad import Textbox
from curses.panel import panel, new_panel, update_panels

# update statusline
def update_statusline(screen_num, screen, win_num, len_win_rows, status=""):
        s_maxy, s_maxx = screen.getmaxyx()
        # statuline string
        if len(status) > 0:
                statusline = '### Error: ' + status + ' '
        else:
                statusline = '### Screen '+ str(screen_num) + ' Window ' + str(win_num) + ' '
        # redraw bottom hline
        if len_win_rows < 3:
                screen.insstr(s_maxy-2, 0, statusline)
                screen.hline(s_maxy-2, len(statusline) , '#', s_maxx)
        else:
                screen.insstr(y_len*(len_win_rows-1)+len_win_rows-2, 0, statusline)
        screen.refresh()
        # return nothing
        return


# redraw screen hlines, vlines
def update_screen(screen_num, screen, win_num, windows):
        screen.clear()
        # get vars
        s_maxy, s_maxx = screen.getmaxyx()
        len_win_rows = len(windows)
        y_len = round((s_maxy-2)/len_win_rows)
        for idx, wins in windows.items():
                # redraw hlines
                if idx < len_win_rows - 1:
                        screen.hline(y_len*(idx+1)+idx, 0, '#', s_maxx)
                # redraw vlines
                maxy, maxx = wins[0].getmaxyx()
                for jdx, w in enumerate(wins):
                        w.refresh()
                        if jdx < len(wins) - 1:
                                screen.vline(y_len*idx+idx, (jdx+1)*maxx+jdx, '#', maxy)
        # update statusline
        update_statusline(screen_num, screen, win_num, len_win_rows)
        update_panels()
        curses.doupdate()
        # return nothing
        return

# horizontally split windows on current screen to have +1 rows
def split_win(screen_num, screens, win_num, windows):
        # clear screen of hlines
        screen = screens[screen_num]
        screen.clear()
        # window to create
        win = None
        # get useful properties
        windows = windows[screen_num]
        len_win_rows = len(windows)
        maxy0, maxx0 = screen.getmaxyx()
        new_y_len = round((maxy0-2)/(len_win_rows+1))
        # loop through windows, resize, move
        for idx, wins in windows.items():
               for jdx, w in enumerate(wins):
                       maxy, maxx = w.getmaxyx()
                       y, x = w.getparyx()
                       w.resize(new_y_len, maxx)
                       w.mvwin(new_y_len*idx+idx, x)
                       w.refresh()
        # create new window
        if len_win_rows > 1:
                new_y_len_bool = True
        else:
                new_y_len_bool = False
        win = screen.subwin(new_y_len-new_y_len_bool, maxx0, len_win_rows*new_y_len+len_win_rows, 0)
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        windows[len_win_rows] = [win]
        text_boxes_text[screen_num][len_win_rows] = [""]
        # update screen
        update_screen(screen_num, screen, win_num, windows)
        # return textbox for editing
        return Textbox(win, insert_mode=True)

# vertically split windows on current window row on current screen to have +1 columns
def vsplit_win(screen_num, screens, win_num, windows):
        # ready the screen, windows
        screen = screens[screen_num]
        screen.clear()
        windows = windows[screen_num]
        win_num_0, win_num_1 = win_num
        wins = windows[win_num_0]
        len_win_cols = len(wins)
        maxy0 = wins[0].getmaxyx()[0]
        s_maxy, s_maxx = screen.getmaxyx()
        # window to create
        win = None
        new_x_len = round(s_maxx/(len_win_cols+1))
        for idx, w in enumerate(wins):
                y, x = w.getparyx()
                maxy, maxx = w.getmaxyx()
                w.resize(maxy, new_x_len-1)
                w.mvwin(y, idx*new_x_len+idx)
                w.refresh()
        win = screen.subwin(maxy0, new_x_len-1, wins[0].getparyx()[0], len_win_cols*new_x_len+len_win_cols)
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        wins.append(win)
        text_boxes_text[screen_num][win_num[0]].append("")
        # update screen
        win_num = [win_num[0], win_num[1]+1]
        update_screen(screen_num, screen, win_num, windows)
        # return text box for editing
        return Textbox(win, insert_mode=True)

# create new screen for editing to have +1 screens
def create_screen(screens, panels, cmdlines, cmds, windows):
        # setup screen
        screens.append(curses.initscr())
        screen = screens[-1]
        panels.append(new_panel(screen))
        panels[-1].top()
        maxy, maxx = screen.getmaxyx()

        # setup cmdline
        cmdlines.append(screen.subwin(1, maxx, maxy-1, 0))
        cmdlines[-1].idcok(True)
        cmds.append(Textbox(cmdlines[-1]))
        cmds[-1].stripspaces = True

        # setup window
        win = screen.subwin(maxy-2, maxx, 0, 0)
        win.idcok(True)
        win.idlok(True)
        win.scrollok(True)
        windows.append({0:[win]})
        text_boxes_text.append({0:[""]})

        # update screen
        win_num = [0, 0]
        update_screen(len(screens)-1, screen, win_num, windows[-1])

        # return text box for text_boxes, and immediate editing
        return Textbox(win, insert_mode=True)

# remove current screen to have -1 screens
def remove_screen(screen_num, screens, panels, cmdlines, cmds, windows, text_boxes):
        # remove screen and associated objects
        del text_boxes_text[screen_num]
        del text_boxes[screen_num]
        del windows[screen_num]
        del cmds[screen_num]
        del cmdlines[screen_num]
        del panels[screen_num]
        del screens[screen_num]
        # get new screen number
        screen_num = 0
        screen = screens[screen_num]
        screen.clear()
        screen.refresh()
        # put screen on top
        panels[screen_num].top()
        # update screen
        win_num = [0, 0]
        update_screen(screen_num, screen, win_num, windows[screen_num])
        # return screen number
        return screen_num

# remove last row of windows on current screen to have -1 rows
def remove_win(screen_num, screens, windows, text_boxes):
        # clear screen of hlines
        screen = screens[screen_num]
        screen.clear()
        # get windows object list
        windows = windows[screen_num]
        # remove last row of windows
        len_win = len(windows)
        del text_boxes_text[screen_num][len_win - 1]
        del text_boxes[screen_num][len_win - 1]
        del windows[len_win - 1]
        # get useful properties
        len_win = len(windows)
        s_maxy, s_maxx = screen.getmaxyx()
        if len_win > 1:
                new_y_len = round((s_maxy-2)/len_win)
        else:
                new_y_len = s_maxy-2
        # loop through windows, moving, resizing
        # somewhat of a hack using idx for precise placement
        for idx, wins in windows.items():
                for jdx, w in enumerate(wins):
                        y, x = w.getparyx()
                        maxy, maxx = w.getmaxyx()
                        if idx > 0:
                                w.mvwin(new_y_len*idx+idx, x)
                        if idx == 2:
                                w.resize(new_y_len-1, maxx)
                        else:
                                w.resize(new_y_len, maxx)
                        w.refresh()
        # update screen
        win_num = [0, 0]
        update_screen(screen_num, screen, win_num, windows)
        # return nothing
        return

# main program loop
def main(stdscr):
        # screen setup
        stdscr.clear()
        screens = []
        panels = []
        cmdlines = []
        cmds = []
        windows = []
        text_boxes = []
        text_boxes_text = []

        # index vars
        screen_num = 0
        win_num = [0, 0]

        # inital text box
        text_boxes.append({0:[create_screen(screens, panels, cmdlines, cmds, windows)]})
        text_boxes[screen_num][win_num[0]][win_num[1]].edit() # Ctrl-g to exit the text_box


        # run the program
        cmds[screen_num].edit()
        c = cmds[screen_num].gather()
        while c != '':
                # new screen
                if c == 'n ':
                        screen_num = len(screens)
                        text_boxes.append({0:[create_screen(screens, panels, cmdlines, cmds, windows)]})
                        win_num = [0, 0]
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # new window
                elif c == 'nw ':
                        # limit horizontal splits to 4
                        if len(windows[screen_num]) < 4:
                                win_num = [len(windows[screen_num]), 0]
                                text_boxes[screen_num][win_num[0]] = [split_win(screen_num, screens, win_num, windows)]
                                text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # new vertical window
                elif c == 'nwv ':
                        len_wins = len(windows[screen_num][win_num[0]])
                        # limit vertical splits to 3
                        if len_wins < 3:
                                text_boxes[screen_num][win_num[0]].append(vsplit_win(screen_num, screens, win_num, windows))
                                win_num = [win_num[0], len_wins]
                                text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # remove screen
                elif c == 'r ':
                        # remove screen if more than one exists
                        if len(screens) > 1:
                                screen_num = remove_screen(screen_num, screens, panels, cmdlines, cmds, windows, text_boxes)
                                win_num = [0, 0]
                        else: # else end program
                                break
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # remove window
                elif c == 'rw ':
                        if len(windows[screen_num]) > 1:
                                remove_win(screen_num, screens, windows, text_boxes)
                                win_num = [0, 0]
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # next screen
                elif c == 's ':
                        # set screen number and screen
                        if screen_num < len(screens) - 1:
                                screen_num += 1
                        else:
                                screen_num = 0
                        screen = screens[screen_num]
                        # push screen to top panel
                        panels[screen_num].top()
                        # reset window numbers
                        win_num = [0, 0]
                        # update screen
                        update_screen(screen_num, screen, win_num, windows[screen_num])
                        # edit default text box
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # next window
                elif c == 'w ':
                        if len(windows[screen_num][win_num[0]]) > 1 and win_num[1] < (len(windows[screen_num][win_num[0]]) - 1):
                                win_num = [win_num[0], win_num[1]+1]
                        elif win_num[0] < (len(windows[screen_num]) - 1):
                                win_num = [win_num[0]+1, 0]
                        else:
                                win_num = [0, 0]
                        # update statusline
                        update_statusline(screen_num, screens[screen_num], win_num, len(windows[screen_num]))
                        # edit correct text box
                        text_boxes[screen_num][win_num[0]][win_num[1]].edit()

                # save to file
                elif c == 'fs ':
                        text_to_save = text_boxes[screen_num][win_num[0]][win_num[1]].gather()
                        cmdlines[screen_num].clear()
                        cmds[screen_num].edit()
                        c = cmds[screen_num].gather()
                        try:
                                with open(c[:-1], 'w') as filename:
                                        filename.write(text_to_save)
                        except:
                                update_statusline(screen_num, screens[screen_num], win_num, len(windows[screen_num]), 'File Save Failed')

                # open file
                elif c == 'fo ':
                        cmdlines[screen_num].clear()
                        cmds[screen_num].edit()
                        c = cmds[screen_num].gather()
                        try:
                                with open(c[:-1], 'r') as filename:
                                        win = windows[screen_num][win_num[0]][win_num[1]]
                                        win.erase()
                                        text_to_insert = filename.readlines()
                                        y, x = win.getparyx()
                                        for idx, textline in enumerate(text_to_insert):
                                                win.addstr(y, x, textline)
                                text_boxes[screen_num][win_num[0]][win_num[1]].edit()
                        except:
                                update_statusline(screen_num, screens[screen_num], win_num, len(windows[screen_num]), 'File Open Failed')

                # get cmd from cmdline
                cmdlines[screen_num].clear()
                cmds[screen_num].edit()
                c = cmds[screen_num].gather()
                # update statusline
                update_statusline(screen_num, screens[screen_num], win_num, len(windows[screen_num]))


        # end program
        curses.endwin()
        return


# entry point for main program, if error, no problem just exit
if __name__ == '__main__':
        wrapper(main)
