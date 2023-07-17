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
        self.line_num = 0
        self.top_line_num = 0
        self.text = []

    # overwrite Textbox do_command for scrolling
    def do_command(self, ch):
        "Process a single editing command."
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        # sanity check
        if self.line_num > len(self.text) - 1:
            for i in range(len(self.text),self.line_num+1):
                self.text.append(' ')
        # print character
        if curses.ascii.isprint(ch):
            if self.text[self.line_num] == '\n' and x != 0:
                self.text[self.line_num] = " " * x
            elif x > len(self.text[self.line_num]):
                self.text[self.line_num] += " " * (x - len(self.text[self.line_num]))
                self.text[self.line_num].lstrip('\n')
            self.text[self.line_num] += chr(ch)
            if x == self.maxx:
                if y == self.maxy:
                    self.win.scroll(1)
                    self.top_line_num += 1
                    self.win.move(y-1, x)
                self._insert_printable_char(ch)
                self.line_num += 1
                if self.line_num < len(self.text):
                    self.win.insstr(self.text[self.line_num])
            else:
                self._insert_printable_char(ch)
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
                    self.top_line_num -= 1
                    self.win.move(y, 0)
                    self.win.insstr(self.text[self.line_num])
                    self.win.move(y, len(self.text[self.line_num]))
            elif self.stripspaces:
                self.win.move(y-1, self._end_of_line(y-1))
                self.line_num -= 1
            else:
                self.win.move(y-1, self.maxx)
                self.line_num -= 1
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
                self.text[self.line_num] = self.text[self.line_num][:x] + self.text[self.line_num][x+1:]
        # Ctrl-d (Delete character under cursor)
        elif ch == curses.ascii.EOT:                           # ^d
            self.win.delch()
            self.text[self.line_num] = self.text[self.line_num][:x] + self.text[self.line_num][x+1:]
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
                self.top_line_num += 1
                self.win.move(y, 0)
                if self.line_num < len(self.text) - 1:
                    self.win.insstr(self.text[self.line_num])
            else:
                self.win.move(y+1, 0)
                self.line_num += 1
            if self.line_num > len(self.text) - 1:
                self.text.append("\n")
        # Ctrl-g (Terminate, returning the window contents)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0           # return zero
        # Ctrl-j (Terminate if the window is 1 line, otherwise insert newline)
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                return 0       # return zero
            self.win.insertln()
            self.win.move(y, 0)
            self.text = self.text[:self.line_num] + [' '] + self.text[self.line_num:]
            if self.line_num > len(self.text) - 1:
                self.text.append(" ")
        # Ctrl-k (If line is blank, delete it, otherwise clear to end of line)
        elif ch == curses.ascii.VT:                            # ^k
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
            self.text[self.line_num] = " "
        # Ctrl-l (Refresh screen)
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        # Ctrl-n (Cursor down, move down one line)
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if y == self.maxy:
                self.win.scroll(1)
                self.line_num += 1
                self.top_line_num += 1
                if self.line_num < len(self.text) - 1:
                    self.win.move(y, 0)
                    self.win.insstr(self.text[self.line_num])
                    self.win.move(y, 0)
                else:
                    self.win.move(y, 0)
                    self.text.append(" ")
            else:
                self.win.move(y+1, x)
                self.line_num += 1
                if self.line_num > len(self.text) - 1:
                    self.text.append(" ")
            if x > len(self.text[self.line_num]):
                self.win.move(y+1, len(self.text[self.line_num]) - 1)
        # Ctrl-o (Insert a blank line at cursor location)
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
            if self.line_num > 0:
                self.text = self.text[:self.line_num] + [" "] + self.text[self.line_num:]
            else:
                self.text = [" "] + self.text
        # Ctrl-p (Cursor up, move up one line)
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if y > 0:
                self.win.move(y-1, x)
                self.line_num -= 1
                if x > len(self.text[self.line_num]) - 1:
                    self.win.move(y-1, len(self.text[self.line_num]) - 1)
            elif self.line_num > 0:
                self.win.scroll(-1)
                self.line_num -= 1
                self.top_line_num -= 1
                self.win.move(y, 0)
                self.win.insstr(self.text[self.line_num])
                self.win.move(y, x)
        # return one
        return 1


def get_cmd(cmdline, cmd):
    "Get a command from commandline"
    cmdline.clear()
    cmdline.refresh()
    return cmd.edit().strip(' ').lower()

def update_statusline(screen_num, screen, status):
    "Update the statusline"
    s_maxy, s_maxx = screen.getmaxyx()
    # statuline string
    if len(status) > 0:
        statusline = '### ' + status + ' '
    else:
        statusline = '### Screen '+ str(screen_num) + ' '
    # redraw bottom hline (statusline)
    screen.insstr(s_maxy-2, 0, statusline)
    screen.hline(s_maxy-2, len(statusline) , '#', s_maxx-len(statusline))
    screen.refresh()
    # return nothing
    return

def update_screen(screen_num, screen, text_box):
    "Redraw the screen"
    screen.clear()
    # redisplay text
    update_text(text_box)
    # update statusline
    update_statusline(screen_num, screen, "")
    # return nothing
    return

def update_text(t_box):
    "Redisplay text box text"
    # display text
    t_box.win.move(0, 0)
    maxy, maxx = t_box.win.getmaxyx()
    minline = t_box.top_line_num
    if maxy < len(t_box.text):
        maxline = minline + maxy
    else:
        maxline = minline + len(t_box.text)
    y, x = [0, 0]
    for line in t_box.text[minline:maxline]:
        while line != "":
            y, x = t_box.win.getyx()
            t_box.win.insstr(line[:maxx])
            if y == maxy - 1:
                break
            else:
                t_box.win.move(y+1, 0)
            line = line[maxx:]
    t_box.line_num = t_box.top_line_num
    t_box.win.move(0, 0)
    t_box.win.refresh()
    # return nothing
    return

def edit_default_text_box(text_box):
    "Edit default text box"
    # move cursor to top left corner
    text_box.line_num = text_box.top_line_num
    text_box.win.move(0, 0)
    return text_box.edit()

def create_screen(screens, cmdlines, cmds, text_boxes):
    "Create new screen for editing to have +1 screens"
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
    text_box = ScrollTextbox(win)
    text_boxes.append(text_box)

    # update screen
    screen_num = len(screens) - 1
    update_screen(screen_num, screen, text_boxes[-1])

    # return screen number
    return screen_num

def remove_screen(screen_num, screens, cmdlines, cmds, text_boxes):
    "Remove current screen to have -1 screens"
    # remove screen and associated objects
    screens[screen_num].clear()
    screens[screen_num].refresh()
    del text_boxes[screen_num]
    del cmds[screen_num]
    del cmdlines[screen_num]
    del screens[screen_num]
    # get new screen number
    screen_num -= 1
    screen = screens[screen_num]
    screen.clear()
    screen.refresh()
    # update screen
    update_screen(screen_num, screen, text_boxes[screen_num])
    # return screen number
    return screen_num

def main(stdscr):
    "Main program loop"
    # screen setup
    stdscr.clear()
    screens = []
    cmdlines = []
    cmds = []
    text_boxes = []

    # inital screen and text box (Ctrl-g to exit the text box)
    screen_num = create_screen(screens, cmdlines, cmds, text_boxes)
    update_statusline(screen_num, screens[screen_num], "Help screen: 'Ctrl-G'+'h'+<Enter>")
    # edit default text box
    edit_default_text_box(text_boxes[screen_num])

    # run the program
    c = ''
    while c != 'q' or c != 'quit' or c != 'exit':
        # get info
        screen = screens[screen_num]
        cmdline = cmdlines[screen_num]
        cmd = cmds[screen_num]
        t_box = text_boxes[screen_num]

        # help buffer display
        if c == 'h' or c == 'help':
            screen_num = create_screen(screens, cmdlines, cmds, text_boxes)
            t_box = text_boxes[-1]
            t_box.text = [
"              Help Page              ",
"-------------------------------------",
"====  Text Box Commands  ====",
"Ctrl-A = Go to left edge of window",
"Ctrl-B = Cursor left, wrapping to previous line if appropriate",
"Ctrl-D = Delete character under cursor",
"Ctrl-E = Go to end of line",
"Ctrl-F = Cursor right, wrapping to next line when appropriate",
"---- Ctrl-G = Go to command line, else if in command line exit ----",
"Ctrl-H = Delete character backward",
"Ctrl-J = Insert newline",
"Ctrl-K = If line is blank, delete it, otherwise clear to end of line",
"Ctrl-L = Refresh text box",
"Ctrl-N = Cursor down; move down one line",
"Ctrl-O = Insert a blank line at cursor location",
"Ctrl-P = Cursor up; move up one line",
"---------------------------------",
"====  Command Line Commands  ====",
"'h[elp]' = display help page",
"'e[dit]' = edit text box",
"'n[ew[ screen]]' = new screen buffer",
"'r[emove[ screen]]' = remove current screen buffer",
"'s[creen]' = go to next screen buffer",
"'f[ile ]s[ave[ as]]' = save to file",
"'f[ile ]o[pen]' = open file",
"'b[uffer]' = list open screen buffers in new screen buffer"
]
            for l,line in enumerate(t_box.text):
                for ch in line:
                    t_box.do_command(ord(ch))
                if l == t_box.win.getmaxyx()[0]:
                    break
            edit_default_text_box(t_box)


        # open buffer screen
        elif c == 'b' or c == 'buffer':
            screen_num = create_screen(screens, cmdlines, cmds, text_boxes)
            t_box = text_boxes[-1]
            t_box.text = [
"==========  Open Screen Buffers  ==========",
" Warning: This buffer will not auto update",
" Recommended to remove when done",
"==========================================="
]
            for s,scrn in enumerate(screens):
                if s == len(screens) - 1:
                    t_box.text.append("* Screen "+str(s)+" * (Buffer Window)")
                else:
                    t_box.text.append("  Screen "+str(s))
            for l,line in enumerate(t_box.text):
                for ch in line:
                    t_box.do_command(ord(ch))
                if l == t_box.win.getmaxyx()[0]:
                    break
            edit_default_text_box(t_box)



        # edit text box
        elif c == 'e' or c == 'edit':
            edit_default_text_box(t_box)


        # new screen
        elif c == 'n' or c == 'new' or c =='new screen':
            screen_num = create_screen(screens, cmdlines, cmds, text_boxes)
            # edit default text box
            edit_default_text_box(text_boxes[screen_num])

        # remove screen
        elif c == 'r' or c == 'remove' or c == 'remove screen':
            # if text box has text, ask
            if len(t_box.text) > 1:
                if len(screens) > 1:
                    update_statusline(screen_num, screen, 'Possibly unsaved work. Remove screen buffer [y/N]?')
                else:
                    # else only one screen buffer
                    update_statusline(screen_num, screen, 'Possibly unsaved work. Quit [y/N]?')
                # get user's choice
                c = get_cmd(cmdlines[screen_num], cmds[screen_num])
                # if user entered yes, and more than one screen buffer, remove current screen buffer
                if 'y' in c and len(screens) > 1:
                    screen_num = remove_screen(screen_num, screens, cmdlines, cmds, text_boxes)
                # else if user entered yes, and only one screen buffer, quit
                elif 'y' in c:
                    break
                # edit text box
                edit_default_text_box(text_boxes[screen_num])
            else: # else remove screen or quit
                if len(screens) > 1:
                    screen_num = remove_screen(screen_num, screens, cmdlines, cmds, text_boxes)
                else:
                    break

        # next screen
        elif c == 's' or c == 'screen':
            # set screen number, screen, and associated windows
            if screen_num < len(screens) - 1:
                screen_num += 1
            else:
                screen_num = 0
            screen = screens[screen_num]
            # update screen
            update_screen(screen_num, screen, text_boxes[screen_num])
            # edit default text box
            edit_default_text_box(text_boxes[screen_num])

        # save to file
        elif c == 'fs' or c == 'file save' or c == 'file save as':
            # update statusline
            update_statusline(screen_num, screen, 'Filename To Save As: ')
            # get filename
            c = get_cmd(cmdline, cmd)
            # try to save file
            try:
                # update statusline
                update_statusline(screen_num, screen, 'Saving File...')
                # save file
                with open(c, 'w') as filename:
                    result = ""
                    for line in t_box.text:
                        if line[-1] == '\n':
                            result += line
                        else:
                            result += line + '\n'
                    filename.write(result)
                # update statusline if successful
                update_statusline(screen_num, screen, 'Save Successful')
                sleep(.1)
                # update statusline
                update_statusline(screen_num, screen, "")
            except: # update statusline if failed
                update_statusline(screen_num, screen, 'Error: File Save Failed')
            # edit default text box with updated statusline
            edit_default_text_box(t_box)

        # open file
        elif c == 'fo' or c == 'file open':
            # update statusline
            update_statusline(screen_num, screen, 'File To Open: ')
            # get filename
            c = get_cmd(cmdline, cmd)
            # try to open file
            t_box = text_boxes[screen_num]
            try:
                filetext = ""
                with open(c, 'r') as filename:
                    filetext = filename.readlines()
                t_box.text = []
                for line in filetext:
                    if line != '\n':
                        t_box.text.append(line.strip('\n'))
                    else:
                        t_box.text.append(line)
                del filetext
                update_screen(screen_num, screen, t_box)
            except: # update statusline if failed
                update_statusline(screen_num, screen, 'Error: File Open Failed')
            # edit default text box
            edit_default_text_box(t_box)


        # get cmd from cmdline
        c = get_cmd(cmdlines[screen_num], cmds[screen_num])
        # check for unsaved work before quitting
        if len(c) < 1:
            flag = False
            for box in text_boxes:
                if len(box.text) > 1:
                    flag = True
            if flag:
                # if text in text boxes, ask if really want to quit
                update_statusline(screen_num, screen, 'Possibly Unsaved Work. Quit Anyways? [y/N]')
                c = get_cmd(cmdlines[screen_num], cmds[screen_num])
                if 'y' in c:
                    break
                else:
                    # else user entered no, edit text box
                    c = 'e'
            else:
                # else if no text in text boxes, end program
                break


    # end program
    curses.endwin()
    return


# entry point for main program, if error, no problem just exit
if __name__ == '__main__':
    wrapper(main)
