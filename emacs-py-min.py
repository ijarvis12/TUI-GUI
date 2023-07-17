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
                        self.text[self.line_num].lstrip('\n')
                        self.text[self.line_num] += " " * (x - len(self.text[self.line_num]))
                self.text[self.line_num].rstrip('\n')
                self.text[self.line_num] += chr(ch)
            elif y == self.maxy:
                self.text[self.line_num] += "\n"
                self.win.scroll(1)
                self.line_num += 1
                self.win.move(y, 0)
                self._insert_printable_char(ch)
                if self.line_num > len(self.text) - 1:
                    self.text.append(chr(ch))
                else:
                    self.text[self.line_num] = chr(ch) + self.text[self.line_num]
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
                    self.win.insstr(self.text[self.line_num])
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
            elif y < self.maxy:
                self.win.move(y+1, 0)
                self.line_num += 1
            elif y == self.maxy:
                self.win.scroll(1)
                self.line_num += 1
                self.win.move(y, 0)
                if self.line_num < len(self.text) - 1:
                    self.win.insstr(self.text[self.line_num])
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
                    self.win.insstr(self.text[self.line_num])
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
                self.text = self.text[0:self.line_num] + ["\n"] + self.text[self.line_num:]
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
                self.win.insstr(self.text[self.line_num])
                self.win.move(y, x)
        # return one
        return 1


def get_cmd(cmdline, cmd):
    "Get a command from commandline"
    cmdline.clear()
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

def update_screen(screen_num, screen, t_box):
    "Redraw the screen"
    screen.clear()
    # redisplay text
    update_text(screen, t_box)
    # update statusline
    update_statusline(screen_num, screen, "")
    # return nothing
    return

def scroll_a_line(box):
    "Function for update_text, and misc buffers; scrolls one line"
    y, x = box.win.getyx()
    maxy, maxx = box.win.getmaxyx()
    if y == maxy-1:
        box.win.scroll(1)
        box.win.move(y, 0)
    else:
        box.win.move(y+1, 0)

def update_text(screen, t_box):
    "Redisplay text box text"
    # clear out text box
    t_box.win.erase()
    # get text_boxes
    t_box.win.move(0, 0)
    # display text
    maxy, maxx = t_box.win.getmaxyx()
    t_box.line_num -= 5
    if t_box.line_num < 0:
        t_box.line_num = 0
    for line in t_box.text[t_box.line_num:]:
        y, x = t_box.win.getyx()
        if y == maxy:
            t_box.win.move(0, 0)
            t_box.line_num -= y
            break
        while line != "":
            for ch in line[:maxx]:
                t_box.win.insstr(ch)
                t_box.win.move(y, x+1)
            scroll_a_line(t_box)
            line = line[maxx:]
            if t_box.line_num < len(t_box.text) - 1:
                t_box.line_num += 1
    t_box.win.refresh()
    screen.refresh()
    # return nothing
    return

def edit_default_text_box(text_box):
    "Edit default text box"
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
    update_screen(len(screens)-1, screen, text_boxes[-1])

    # return nothing
    return

def remove_screen(screen_num, screens, cmdlines, cmds, text_boxes):
    "Remove current screen to have -1 screens"
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
    screen_num = len(screens)
    create_screen(screens, cmdlines, cmds, text_boxes)
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
            create_screen(screens, cmdlines, cmds, text_boxes)
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
                if l == len(t_box.text) - 1:
                    break
                else:
                    scroll_a_line(t_box)
            edit_default_text_box(t_box)


        # open buffer screen
        elif c == 'b' or c == 'buffer':
            create_screen(screens, cmdlines, cmds, text_boxes)
            t_box = text_boxes[-1]
            t_box.text = [
"=========  Open Screen Buffers  =========",
"Warning: This buffer will not auto update",
"Recommended to remove when done"
]
            for s,scrn in enumerate(screens):
                if s == len(screens) - 1:
                    t_box.text.append("* Screen "+str(s)+" * (Buffer Window)")
                else:
                    t_box.text.append("  Screen "+str(s))
            for l,line in enumerate(t_box.text):
                for ch in line:
                    t_box.do_command(ord(ch))
                if l == len(t_box.text) - 1:
                    break
                else:
                    scroll_a_line(t_box)
            edit_default_text_box(t_box)



        # edit text box
        elif c == 'e' or c == 'edit':
            edit_default_text_box(t_box)


        # new screen
        elif c == 'n' or c == 'new' or c =='new screen':
            screen_num = len(screens)
            create_screen(screens, cmdlines, cmds, text_boxes)
            # edit default text box
            edit_default_text_box(text_boxes[screen_num])

        # remove screen
        elif c == 'r' or c == 'remove' or c == 'remove screen':
            # if text box has text, ask
            if len(t_box) > 1:
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
                else:
                    # else user entered no, edit text box
                    edit_default_text_box(t_box)
            else: # else end program
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
            # get text box text to save
            text_to_save = t_box.text
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
                    for line in text_to_save:
                        if line[-1] == '\n':
                            result += line
                        else:
                            result += line + '\n'
                    filename.write(result)
                # update statusline if successful
                update_statusline(screen_num, screen, 'Save Successful')
                # update statusline
                sleep(.1)
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
                with open(c, 'r') as filename:
                    text_to_insert = filename.readlines()
                    t_box.win.erase()
                    t_box.text = ['\n']
                    for textline in text_to_insert:
                        for ch in textline:
                            t_box.do_command(ord(ch))
                # update statusline
                update_statusline(screen_num, screen, "")
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
