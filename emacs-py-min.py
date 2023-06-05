#!/usr/bin/env python3

import curses
from curses import wrapper, window
from curses.textpad import Textbox

from time import sleep


class ScrollTextbox(Textbox):
    def __init__(self, win, insert_mode=False):
            super().__init__(win, insert_mode)
            self.win.idcok(True)
            self.win.idlok(True)
            self.win.scrollok(True)
            self.stripspaces = True
            self.line_num = self.win.getyx()[0]
            self.text = []
            for i in range(self.line_num):
                self.text.append('\n')

    # overwrite Textbox do_command for scrolling
    def do_command(self, ch):
        "Process a single editing command."
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        # sanity check
        if self.line_num > len(self.text) - 1:
            for i in range(len(self.text),self.line_num+1):
                self.text.append('\n')
        # print character
        if curses.ascii.isprint(ch):
            if y < self.maxy or x < self.maxx:
                self._insert_printable_char(ch)
                if self.text[self.line_num] == '\n':
                    if x == 0:
                        self.text[self.line_num] = ""
                    else:
                        self.text[self.line_num] = " " * x
                elif x > len(self.text[self.line_num]):
                        self.text[self.line_num] += " " * (x - len(self.text[self.line_num]))
                self.text[self.line_num] += chr(ch)
            elif y == self.maxy:
                self.text[self.line_num] += "\n"
                self.win.scroll(1)
                self.line_num += 1
                self.win.move(y, 0)
                self._insert_printable_char(ch)
                self.text.append(chr(ch))
        # Ctrl-a (Go to left edge of window)
        elif ch == curses.ascii.SOH:                           # ^a
            self.win.move(y, 0)
        # Ctrl-b (Cursor left, wrapping to previous line if appropriate (backspace doesn't work))
        elif ch in (curses.ascii.STX, curses.KEY_LEFT, curses.ascii.BS, curses.KEY_BACKSPACE):     # ^b
            if x > 0:
                self.win.move(y, x-1)
            elif y == 0:
                if self.line_num > 0:
                    self.win.scroll(-1)
                    self.line_num -= 1
                    self.win.move(y, 0)
                    for s in self.text[self.line_num]:
                        self._insert_printable_char(ord(s))
                    self.win.move(y, x)
            elif self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
                self.line_num -= 1
            else:
                self.win.move(y-1, self.maxx)
                self.line_num -= 1
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
                self.text[self.line_num] = self.text[self.line_num][0:x] + self.text[self.line_num][x+1:]
        # Ctrl-d (Delete character under cursor)
        elif ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
            self.text[self.line_num] = self.text[self.line_num][0:x] + self.text[self.line_num][x+1:]
        # Ctrl-e (Go to right edge (stripspaces off) or end of line (stripspaces on))
        elif ch == curses.ascii.ENQ:                           # ^e
            if self.stripspaces:
                self.win.move(y, self._end_of_line(y))
            else:
                self.win.move(y, self.maxx)
        # Ctrl-f (Cursor right, wrapping to next line when appropriate)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            if x < self.maxx:
                self.win.move(y, x+1)
            elif y == self.maxy:
                self.win.scroll(1)
                self.line_num += 1
                self.win.move(y, 0)
            else:
                self.win.move(y+1, 0)
                self.line_num += 1
            if self.line_num > len(self.text) - 1:
                self.text.append("\n")
        # Ctrl-g (Terminate, returning the window contents)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0
        # Ctrl-j (Terminate if the window is 1 line, otherwise insert newline)
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                # return zero
                return 0
            elif y < self.maxy:
                self.win.move(y+1, 0)
                self.line_num += 1
            elif y == self.maxy:
                self.win.scroll(1)
                self.line_num += 1
                self.win.move(y, 0)
            if self.line_num > len(self.text) - 1:
                self.text.append("\n")
        # Ctrl-k (If line is blank, delete it, otherwise clear to end of line)
        elif ch == curses.ascii.VT:                            # ^k
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
            self.text[self.line_num] = "\n"
        # Ctrl-l (Refresh screen)
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        # Ctrl-n (Cursor down, move down one line)
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if y == self.maxy:
                self.win.scroll(1)
                self.line_num += 1
                if self.line_num < len(self.text) - 1:
                    self.win.move(y, 0)
                    for s in self.text[self.line_num]:
                        self._insert_printable_char(ord(s))
                    self.win.move(y, x)
                else:
                    self.win.move(y, 0)
                    self.text.append("\n")
            else:
                self.win.move(y+1, x)
                self.line_num += 1
                if self.line_num > len(self.text) - 1:
                    self.text.append("\n")
            if x > self._end_of_line(y+1):
                self.win.move(y+1, self._end_of_line(y+1))
        # Ctrl-o (Insert a blank line at cursor location)
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
            if self.line_num > 0:
                self.text = self.text[self.line_num-1:self.line_num] + ["\n"] + self.text[self.line_num:]
            else:
                self.text = ["\n"] + self.text
        # Ctrl-p (Cursor up, move up one line)
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if y > 0:
                self.win.move(y-1, x)
                self.line_num -= 1
                if x > self._end_of_line(y-1):
                    self.win.move(y-1, self._end_of_line(y-1))
            elif self.line_num > 0:
                self.win.scroll(-1)
                self.line_num -= 1
                self.win.move(y, 0)
                for s in self.text[self.line_num]:
                    self._insert_printable_char(ord(s))
                self.win.move(y, x)
        # return one
        return 1


# get command from commandline
def get_cmd(cmdline, cmd):
    cmdline.clear()
    return cmd.edit().strip(' ').lower()

# update statusline
def update_statusline(screen_num, screen, win_num, len_win_rows, status):
    s_maxy, s_maxx = screen.getmaxyx()
    y_len = round((s_maxy-2)/len_win_rows)
    # statuline string
    if len(status) > 0:
        statusline = '### ' + status + ' '
    else:
        statusline = '### Screen '+ str(screen_num) + ' Window ' + str(win_num) + ' '
    # redraw bottom hline (statusline)
    screen.insstr(s_maxy-2, 0, statusline)
    screen.hline(s_maxy-2, len(statusline) , '#', s_maxx-len(statusline))
    screen.refresh()
    # return nothing
    return

# redraw screen hlines, vlines
def update_screen(screen_num, screen, win_num, text_boxes):
    screen.clear()
    # get vars
    s_maxy, s_maxx = screen.getmaxyx()
    len_win_rows = len(text_boxes)
    y_len = round((s_maxy-2)/len_win_rows)
    for idx, t_boxes in text_boxes.items():
        # redraw hlines
        if idx < len_win_rows - 1:
            screen.hline(y_len*(idx+1)+idx, 0, '#', s_maxx)
        # redraw vlines
        maxy, maxx = t_boxes[0].win.getmaxyx()
        for jdx, box in enumerate(t_boxes):
            if jdx < len(t_boxes) - 1:
                screen.vline(y_len*idx+idx, (jdx+1)*maxx+jdx, '#', maxy)
    # update statusline
    update_statusline(screen_num, screen, win_num, len_win_rows, "")
    # redisplay text
    update_text(screen, text_boxes)
    # return nothing
    return

# redisplay text boxes text
def update_text(screen, text_boxes):
    # get text_boxes
    for win_row, t_boxes in text_boxes.items():
        for box in t_boxes:
            # move to beginning of window
            box.win.move(0, 0)
            # display text
            box.line_num = 0
            maxy, maxx = box.win.getmaxyx()
            for line in box.text:
                y, x = box.win.getyx()
                if y == maxy-1:
                    box.win.scroll(1)
                    box.line_num += 1
                    box.win.move(y, 0)
                for ch in line:
                    box._insert_printable_char(ord(ch))
                box.win.move(y+1, 0)
                box.line_num += 1
            box.win.refresh()
            box.win.move(0, 0)
    screen.refresh()
    # return nothing
    return

# edit default text box
def edit_default_text_box(text_box):
    text_box.win.move(0, 0)
    text_box.do_command(curses.KEY_UP)
    return text_box.edit()

# horizontally split windows on current screen to have +1 rows
def split_win(screen_num, screen, win_num, text_boxes):
    # clear screen of hlines, vlines
    screen.clear()
    # window to create
    win = None
    # get useful properties
    len_win_rows = len(text_boxes[screen_num])
    maxy0, maxx0 = screen.getmaxyx()
    new_y_len = round((maxy0-2)/(len_win_rows+1))
    # loop through windows, resize, move
    for idx, t_boxes in text_boxes[screen_num].items():
       for box in t_boxes:
           maxy, maxx = box.win.getmaxyx()
           y, x = box.win.getparyx()
           box.win.resize(new_y_len, maxx)
           box.win.mvwin(new_y_len*idx+idx, x)
           box.win.refresh()
    # create new window
    if len_win_rows > 1:
        new_y_len_bool = True
    else:
        new_y_len_bool = False
    win = screen.subwin(new_y_len-new_y_len_bool, maxx0, len_win_rows*new_y_len+len_win_rows, 0)
    text_box = ScrollTextbox(win)
    text_boxes[screen_num][win_num[0]] = [text_box]
    # update screen
    update_screen(screen_num, screen, win_num, text_boxes[screen_num])
    # return nothing
    return

# vertically split windows on current window row on current screen to have +1 columns
def vsplit_win(screen_num, screen, win_num, text_boxes):
    # ready the screen, windows
    screen.clear()
    win_num_0, win_num_1 = win_num
    boxes = text_boxes[screen_num][win_num_0]
    len_win_cols = len(boxes)
    maxy0 = boxes[0].win.getmaxyx()[0]
    s_maxy, s_maxx = screen.getmaxyx()
    # window to create
    win = None
    new_x_len = round(s_maxx/(len_win_cols+1))
    for idx, box in enumerate(boxes):
        y, x = box.win.getparyx()
        maxy, maxx = box.win.getmaxyx()
        box.win.resize(maxy, new_x_len-1)
        box.win.mvwin(y, idx*new_x_len+idx)
        box.win.refresh()
    win = screen.subwin(maxy0, new_x_len-1, boxes[0].win.getparyx()[0], len_win_cols*new_x_len+len_win_cols)
    text_box = ScrollTextbox(win)
    text_boxes[screen_num][win_num[0]].append(text_box)
    # update screen
    update_screen(screen_num, screen, win_num, text_boxes[screen_num])
    # return nothing
    return

# create new screen for editing to have +1 screens
def create_screen(screens, cmdlines, cmds, text_boxes):
    # setup screen
    screens.append(curses.initscr())
    screen = screens[-1]
    maxy, maxx = screen.getmaxyx()

    # setup cmdline
    cmdlines.append(screen.subwin(1, maxx, maxy-1, 0))
    cmdlines[-1].idcok(True)
    cmds.append(Textbox(cmdlines[-1]))
    cmds[-1].stripspaces = True

    # setup window
    win = screen.subwin(maxy-2, maxx, 0, 0)
    #windows.append({0:[win]})
    text_box = ScrollTextbox(win)
    text_boxes.append({0:[text_box]})

    # update screen
    win_num = [0, 0]
    update_screen(len(screens)-1, screen, win_num, text_boxes[-1])

    # return nothing
    return

# remove current screen to have -1 screens
def remove_screen(screen_num, screens, cmdlines, cmds, text_boxes):
    # remove screen and associated objects
    del text_boxes[screen_num]
    del cmds[screen_num]
    del cmdlines[screen_num]
    del screens[screen_num]
    # get new screen number
    screen_num = 0
    screen = screens[screen_num]
    screen.clear()
    screen.refresh()
    # update screen
    win_num = [0, 0]
    update_screen(screen_num, screen, win_num, text_boxes[screen_num])
    # return screen number
    return screen_num

# remove last row of windows on current screen to have -1 rows
def remove_win(screen_num, screen, text_boxes):
    # clear screen of hlines
    screen.clear()
    # remove last row of windows
    len_win = len(text_boxes[screen_num])
    del text_boxes[screen_num][len_win - 1]
    #del windows[len_win - 1]
    # get useful properties
    len_win = len(text_boxes[screen_num])
    s_maxy, s_maxx = screen.getmaxyx()
    if len_win > 1:
        new_y_len = round((s_maxy-2)/len_win)
    else:
        new_y_len = s_maxy-2
    # loop through windows, moving, resizing
    # somewhat of a hack using idx for precise placement
    for idx, t_boxes in text_boxes[screen_num].items():
        for box in t_boxes:
            y, x = box.win.getparyx()
            maxy, maxx = box.win.getmaxyx()
            if idx > 0:
                box.win.mvwin(new_y_len*idx+idx, x)
            box.win.resize(new_y_len, maxx)
            box.win.refresh()
    # update screen
    win_num = [0, 0]
    update_screen(screen_num, screen, win_num, text_boxes[screen_num])
    # return nothing
    return

# main program loop
def main(stdscr):
    # screen setup
    stdscr.clear()
    screens = []
    cmdlines = []
    cmds = []
    text_boxes = []

    # index vars
    screen_num = 0
    win_num = [0, 0]

    # inital screen and text box (Ctrl-g to exit the text box)
    #create_screen(screens, cmdlines, cmds, text_boxes)
    #text_boxes[screen_num][win_num[0]][win_num[1]].edit()
    c = 'new screen'

    # run the program
    while c != 'q' or c != 'quit' or c != 'exit':
        # get info
        try:
            screen = screens[screen_num]
            cmdline = cmdlines[screen_num]
            cmd = cmds[screen_num]
            t_boxes = text_boxes[screen_num]
        except:
            pass

        # edit window number #[,#]
        if c == 'e' or c == 'edit':
            # update statusline
            update_statusline(screen_num, screen, win_num, len(t_boxes), 'Enter Window Number #[,#] To Edit:')
            # get window number(s)
            c = get_cmd(cmdline, cmd)
            # try to edit window number, if exists
            try:
                if len(c) > 1:
                    win_num = [int(c[0]), int(c[2])]
                else:
                    win_num = [int(c[0]), 0]
            except: # update statusline if bad number
                update_statusline(screen_num, screen, win_num, len(t_boxes), 'Window Does Not Exist')
            finally: # edit default text box
                edit_default_text_box(text_boxes[screen_num][win_num[0]][win_num[1]])


        # new screen
        elif c == 'n' or c == 'new' or c =='new screen':
            screen_num = len(screens)
            create_screen(screens, cmdlines, cmds, text_boxes)
            win_num = [0, 0]
            text_boxes[screen_num][win_num[0]][win_num[1]].edit()

        # new window
        elif c == 'nw' or c =='new win' or c == 'new window':
            # limit horizontal splits to 2
            len_wins = len(t_boxes)
            if len_wins < 2:
                win_num = [len_wins, 0]
                split_win(screen_num, screen, win_num, text_boxes)
            # edit default text box
            edit_default_text_box(text_boxes[screen_num][win_num[0]][win_num[1]])


        # new vertical window
        elif c == 'nwv' or c == 'new win vert' or c == 'new window vertical':
            # limit vertical splits to 2
            len_wins = len(t_boxes[win_num[0]])
            if len_wins < 2:
                win_num = [win_num[0], len_wins]
                vsplit_win(screen_num, screen, win_num, text_boxes)
            # edit default text box
            edit_default_text_box(text_boxes[screen_num][win_num[0]][win_num[1]])


        # remove screen
        elif c == 'r' or c == 'remove' or c == 'remove screen':
            # remove screen if more than one exists
            if len(screens) > 1:
                screen_num = remove_screen(screen_num, screens, cmdlines, cmds, text_boxes)
                win_num = [0, 0]
                # edit text box
                edit_default_text_box(text_boxes[screen_num][win_num[0]][win_num[1]])
            else: # else end program
                break

        # remove window
        elif c == 'rw' or c == 'remove win' or c == 'remove window':
            if len(t_boxes) > 1:
                remove_win(screen_num, screen, text_boxes)
                win_num = [0, 0]
            # edit default text box
            edit_default_text_box(text_boxes[screen_num][win_num[0]][win_num[1]])

        # next screen
        elif c == 's' or c == 'screen':
            #set screen number, screen, and associated windows
            if screen_num < len(screens) - 1:
                screen_num += 1
            else:
                screen_num = 0
            screen = screens[screen_num]
            # reset window numbers
            win_num = [0, 0]
            # update screen
            update_screen(screen_num, screen, win_num, text_boxes[screen_num])
            # edit default text box
            edit_default_text_box(text_box = text_boxes[screen_num][win_num[0]][win_num[1]])

        # next window
        elif c == 'w' or c == 'win' or c == 'window':
            # window number arithmetic
            if len(t_boxes[win_num[0]]) > 1 and win_num[1] < (len(t_boxes[win_num[0]]) - 1):
                win_num = [win_num[0], win_num[1]+1]
            elif win_num[0] < (len(t_boxes) - 1):
                win_num = [win_num[0]+1, 0]
            else:
                win_num = [0, 0]
            # update statusline
            update_statusline(screen_num, screen, win_num, len(t_boxes), "")
            # edit correct text box
            edit_default_text_box(text_boxes[screen_num][win_num[0]][win_num[1]])

        # save to file
        elif c == 'fs' or c == 'file save' or c == 'file save as':
            # get text box text to save
            text_to_save = text_boxes[screen_num][win_num[0]][win_num[1]].text
            # update statusline
            update_statusline(screen_num, screen, win_num, len(t_boxes), 'Filename To Save Window '+str(win_num)+' As: ')
            # get filename
            c = get_cmd(cmdline, cmd)
            # try to save file
            try:
                # update statusline
                update_statusline(screen_num, screen, win_num, len(t_boxes), 'Saving File...')
                # save file
                with open(c, 'w') as filename:
                    result = ""
                    for line in text_to_save:
                        result += line
                    filename.write(result)
                # update statusline if successful
                update_statusline(screen_num, screen, win_num, len(t_boxes), 'Save Successful')
                # update statusline
                sleep(1)
                update_statusline(screen_num, screen, win_num, len(t_boxes), "")
                # edit default text box with updated statusline
                text_boxes[screen_num][win_num[0]][win_num[1]].edit()
            except: # update statusline if failed
                update_statusline(screen_num, screen, win_num, len(t_boxes), 'Error: File Save Failed')

        # open file
        elif c == 'fo' or c == 'file open':
            # update statusline
            update_statusline(screen_num, screen, win_num, len(t_boxes), 'File To Open: ')
            # get filename
            c = get_cmd(cmdline, cmd)
            # try to open file
            text_box = text_boxes[screen_num][win_num[0]][win_num[1]]
            try:
                with open(c, 'r') as filename:
                    text_to_insert = filename.readlines()
                    text_box.win.erase()
                    text_box.text = ['\n']
                    for textline in text_to_insert:
                        for ch in textline:
                            text_box.do_command(ord(ch))
                # update statusline
                update_statusline(screen_num, screen, win_num, len(t_boxes), "")
            except: # update statusline if failed
                update_statusline(screen_num, screen, win_num, len(t_boxes), 'Error: File Open Failed')
            # edit default text box
            text_box.edit()

        # get cmd from cmdline
        c = get_cmd(cmdlines[screen_num], cmds[screen_num])
        # check for unsaved work before quitting
        if len(c) < 1:
            flag = False
            for screen_text in text_boxes:
                for idx, t_boxes in screen_text.items():
                    for box in t_boxes:
                        if len(box.text) > 1:
                            flag = True
            if flag:
                update_statusline(screen_num, screen, win_num, len(t_boxes), 'Possibly Unsaved Work. Quit Anyways? [y/N] ')
                c = get_cmd(cmdlines[screen_num], cmds[screen_num])
                if 'y' in c:
                    # end program
                    curses.endwin()
                    return
                else:
                    c = 'e'


    # end program
    curses.endwin()
    return


# entry point for main program, if error, no problem just exit
if __name__ == '__main__':
    wrapper(main)
