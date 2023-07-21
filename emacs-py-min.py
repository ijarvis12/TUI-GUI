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
        self.text = [""]

    # overwrite Textbox do_command for scrolling
    def do_command(self, ch):
        "Process a single editing command."
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.lastcmd = ch
        # print character
        if curses.ascii.isprint(ch):
            if x > len(self.text[self.line_num]):
                self.text[self.line_num] += " " * (x - len(self.text[self.line_num]))
            self.text[self.line_num] += chr(ch)
            if x == self.maxx:
                if y == self.maxy:
                    self.win.scroll(1)
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
                if self.line_num < len(self.text):
                    self.win.insstr(self.text[self.line_num])
            else:
                self.win.move(y+1, 0)
                self.line_num += 1
            if self.line_num > len(self.text) - 1:
                self.text.append("")
        # Ctrl-g (Terminate, returning the window contents)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0           # return zero
        # Ctrl-j (Terminate if the window is 1 line, otherwise insert newline)
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                return 0       # return zero
            self.win.move(y+1, 0)
            self.win.insertln()
            self.text = self.text[:self.line_num] + [""] + self.text[self.line_num:]
            self.line_num += 1
            if self.line_num > len(self.text) - 1:
                self.text.append("")
        # Ctrl-k (If line is blank, delete it, otherwise clear to end of line)
        elif ch == curses.ascii.VT:                            # ^k
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
            self.text[self.line_num] = ""
        # Ctrl-l (Refresh buffer)
        elif ch == curses.ascii.FF:                            # ^l
            self.win.refresh()
        # Ctrl-n (Cursor down, move down one line)
        elif ch in (curses.ascii.SO, curses.KEY_DOWN):         # ^n
            if y == self.maxy:
                self.win.scroll(1)
                self.line_num += 1
                self.top_line_num += 1
                self.win.move(y, 0)
                if self.line_num < len(self.text):
                    self.win.insstr(self.text[self.line_num])
                else:
                    self.text.append("")
                self.win.move(y, x)
            else:
                self.win.move(y+1, x)
                self.line_num += 1
                # sanity check #
                if self.line_num > len(self.text) - 1:
                    for i in range(len(self.text),self.line_num+1):
                        self.text.append("")
                # end sanity check #
            if x > len(self.text[self.line_num]):
                self.win.move(y+1, len(self.text[self.line_num]))
        # Ctrl-o (Insert a blank line at cursor location)
        elif ch == curses.ascii.SI:                            # ^o
            self.win.insertln()
            if self.line_num > 0:
                self.text = self.text[:self.line_num] + [""] + self.text[self.line_num:]
            else:
                self.text = [""] + self.text
            self.win.move(y, 0)
        # Ctrl-p (Cursor up, move up one line)
        elif ch in (curses.ascii.DLE, curses.KEY_UP):          # ^p
            if y > 0:
                self.win.move(y-1, x)
                self.line_num -= 1
            elif self.line_num > 0:
                self.win.scroll(-1)
                self.line_num -= 1
                self.top_line_num -= 1
                self.win.move(y, 0)
                self.win.insstr(self.text[self.line_num])
                self.win.move(y, x)
            if x > len(self.text[self.line_num]):
                self.win.move(y-1, len(self.text[self.line_num]))
        # return one
        return 1


class Buffer():
    def __init__(self):
        "Create new buffer for editing to have +1 buffers"
        # setup buffer
        self.screen = curses.initscr()
        maxy, maxx = self.screen.getmaxyx()

        # setup cmdline
        cmdline = self.screen.subwin(1, maxx, maxy-1, 0)
        cmdline.idcok(True)
        self.cmd = Textbox(cmdline)
        self.cmd.stripspaces = True

        # setup text box
        win = self.screen.subwin(maxy-2, maxx, 0, 0)
        self.text_box = ScrollTextbox(win)
        self.save_needed = False

    def toggle_save_needed(self, bool):
        "Set save_needed bool"
        self.save_needed = bool
        # return nothing
        return


class Buffers():
    def __init__(self):
        "Initialize the Application"
        self.buffers = [Buffer()]
        self.buffer_num = 0
        self.current_buffer = self.buffers[0]

    def add_buffer(self):
        "Add a buffer"
        self.buffers.append(Buffer())
        self.buffer_num = len(self.buffers) - 1
        self.current_buffer = self.buffers[-1]

    def get_cmd(self):
        "Get a command from commandline"
        self.current_buffer.cmd.win.clear()
        self.current_buffer.cmd.win.refresh()
        return self.current_buffer.cmd.edit().strip(' ').lower()

    def update_statusline(self, status):
        "Update the statusline"
        current_buffer = self.current_buffer
        screen = current_buffer.screen
        s_maxy, s_maxx = screen.getmaxyx()
        # statuline string
        if len(status) > 0:
            statusline = '### ' + status + ' '
        else:
            statusline = '### Buffer '+ str(self.buffer_num) + ' ' + '# Row ' + str(current_buffer.text_box.line_num) + ' Col ' + str(current_buffer.text_box.win.getyx()[1]) + ' '
        # redraw bottom hline (statusline)
        screen.insstr(s_maxy-2, 0, statusline)
        screen.hline(s_maxy-2, len(statusline) , '#', s_maxx-len(statusline))
        screen.refresh()
        # return nothing
        return

    def update_text(self):
        "Redisplay text box text"
        t_box = self.current_buffer.text_box
        # display text
        t_box.win.move(0, 0)
        maxy, maxx = t_box.win.getmaxyx()
        minline = t_box.top_line_num
        if maxy < len(t_box.text):
            maxline = minline + maxy
        else:
            maxline = minline + len(t_box.text)
        for line in t_box.text[minline:maxline+1]:
            y, x = t_box.win.getyx()
            t_box.win.insstr(line)
            if y == maxy - 1:
                break
            else:
                t_box.win.move(y+1, 0)
        t_box.line_num = t_box.top_line_num
        t_box.win.move(0, 0)
        t_box.win.refresh()
        # return nothing
        return

    def update_buffer(self, buffer_num=-1):
        "Redraw the buffer"
        if buffer_num > -1: # if buffer number is not -1, update the buffer number and current buffer
            # Update the buffer number
            self.buffer_num = buffer_num
            self.current_buffer = self.buffers[buffer_num]
        self.current_buffer.screen.clear()
        # redisplay text
        self.update_text()
        # update statusline
        self.update_statusline("")
        # return nothing
        return

    def edit_default_text_box(self):
        "Edit default text box"
        text_box = self.current_buffer.text_box
        # move cursor to top left corner
        text_box.line_num = text_box.top_line_num
        text_box.win.move(0, 0)
        # edit text box
        return text_box.edit()

    def del_buffer(self):
        "Delete current buffer and update buffer number (and current buffer)"
        # remove buffer and associated objects
        self.current_buffer.screen.clear()
        self.current_buffer.screen.refresh()
        del self.buffers[self.buffer_num]
        # update buffer number (and buffer)
        if self.buffer_num > 0:
            self.update_buffer(self.buffer_num - 1)
        else:
            self.update_buffer(0)
        # return nothing
        return


    def remove_buffer(self):
        "Remove current buffer to have -1 buffers or quit"
        # if more than one buffer...
        if len(self.buffers) > 1:
            # if the buffer has unsaved work, ask about removing
            if self.current_buffer.save_needed:
                self.update_statusline('Unsaved work. Remove buffer [y/N]?')
                # get user's choice
                cmd = self.get_cmd()
                if 'y' in cmd: # if user entered yes, remove buffer
                    self.del_buffer()
            else: # else buffer has no unsaved work, safe to remove
                self.del_buffer()
        else: # else if only buffer...
            # if unsaved work, ask
            if self.current_buffer.save_needed:
                self.update_statusline('Unsaved work. Quit [y/N]?')
                # get user's choice
                cmd = self.get_cmd()
                if 'y' in cmd: # if user entered yes, quit
                    curses.endwin()
                    exit()
            else: # else no unsaved work, quit
                curses.endwin()
                exit()
        # return nothing
        return


### MAIN PROGRAM ###
def main(stdscr):
    "Main program loop"

    ### start of buffers setup ###
    stdscr.clear()
    # inital buffer and text box (Ctrl-g to exit the text box)
    emacs = Buffers()
    # update buffer
    emacs.update_buffer()
    emacs.update_statusline("Help buffer: 'Ctrl-G'+'h'+<Enter>")
    ### end buffers setup ###

    ### start of program while loop ###
    # to start, edit default text box
    cmd = 'edit'
    while cmd != 'q' and cmd != 'quit' and cmd != 'exit':
        # get info
        buffer = emacs.current_buffer
        t_box = buffer.text_box


        # COMMAND: help buffer display
        if cmd == 'h' or cmd == 'help':
            emacs.add_buffer()
            # update buffer
            emacs.update_buffer()
            # set text box help text
            t_box = emacs.current_buffer.text_box
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
"'n[ew[ buffer]]' = new buffer",
"'r[emove[ buffer]]' = remove current buffer",
"'b[uffer]' = go to next buffer",
"'f[ile ]s[ave[ as]]' = save to file",
"'f[ile ]o[pen]' = open file",
"'o[pen buffers]' = list open buffers in new buffer"
]
            # display help text
            t_box.win.move(0, 0)
            for l,line in enumerate(t_box.text):
                t_box.win.insstr(l, 0, line)
                if l == t_box.win.getmaxyx()[0]:
                    break
            # edit the text box
            emacs.edit_default_text_box()


        # COMMAND: open buffer with numbered open buffers
        elif cmd == 'o' or cmd == 'open buffers':
            emacs.add_buffer()
            # update buffer
            emacs.update_buffer()
            # set text box header text
            t_box = emacs.current_buffer.text_box
            t_box.text = [
"==========  Open buffer Buffers  ==========",
" Warning: This buffer will not auto update ",
"      Recommended to remove when done      ",
"==========================================="
]
            # get open buffers
            for b,buff in enumerate(emacs.buffers):
                if b == len(emacs.buffers) - 1:
                    t_box.text.append("* Buffer "+str(b)+" * (Current Buffer)")
                else:
                    t_box.text.append("  Buffer "+str(b))
            # display text box text
            t_box.win.move(0, 0)
            for lnum,line_of_text in enumerate(t_box.text):
                t_box.win.insstr(lnum, 0, line_of_text)
                if lnum == t_box.win.getmaxyx()[0]:
                    break
            # edit the text box
            emacs.edit_default_text_box()


        # COMMAND: edit text box
        elif cmd == 'e' or cmd == 'edit':
            emacs.edit_default_text_box()


        # COMMAND: new buffer
        elif cmd == 'n' or cmd == 'new' or cmd =='new buffer':
            emacs.add_buffer()
            # update buffer
            emacs.update_buffer()
            # edit default text box
            emacs.edit_default_text_box()

        # COMMAND: remove buffer
        elif cmd == 'r' or cmd == 'remove' or cmd == 'remove buffer':
            emacs.remove_buffer()
            # if at least one buffer left, edit default buffer text box
            if emacs:
                emacs.edit_default_text_box()
            else: # else end program
                # break out of while loop to end program
                break


        # COMMAND: next buffer
        elif cmd == 'b' or cmd == 'buffer':
            # set buffer number
            if emacs.buffer_num < len(emacs.buffers) - 1:
                emacs.update_buffer(emacs.buffer_num + 1)
            else:
                emacs.update_buffer(0)
            # edit default text box
            emacs.edit_default_text_box()


        # COMMAND: save to file
        elif cmd == 'fs' or cmd == 'file save' or cmd == 'file save as':
            # update statusline
            emacs.update_statusline('Filename To Save As: ')
            # get filename
            filename = emacs.get_cmd()
            # update statusline
            emacs.update_statusline('Saving File...')
            # get text for saving
            text_to_save = ""
            for line_of_text in t_box.text:
                text_to_save += line_of_text + '\n'

            # try to save file
            try:
                with open(filename, 'w') as file:
                    file.write(text_to_save)
                # update statusline if successful
                emacs.update_statusline('Save Successful')
                # No save needed anymore, at least until another edit
                buffer.toggle_save_needed(False)
                # pause for a tiny bit to show the updated statusline before updating again
                sleep(.1)
                # update statusline
                emacs.update_statusline("")
            except: # update statusline if failed
                emacs.update_statusline('Error: File Save Failed')

           # free up var for memory (could be large file)
            del text_to_save
            # edit default text box with updated statusline
            emacs.edit_default_text_box()


        # COMMAND: open file
        elif cmd == 'fo' or cmd == 'file open':
            # update statusline
            emacs.update_statusline('File To Open: ')
            # get filename
            filename = emacs.get_cmd()
            # var to hold text
            text_from_file = ""

            # try to open file
            try:
                with open(filename, 'r') as file:
                    text_from_file = file.readlines()
            except: # update statusline if failed
                emacs.update_statusline('Error: File Open Failed')

            # if any text read from file, add to buffer
            if len(text_from_file) > 0:
                t_box.text = []
                for line in text_from_file:
                    t_box.text.append(line.strip('\n'))

                # free up var for memory (could be large file)
                del text_from_file

                # update buffer for displaying the text
                emacs.update_buffer()

            # edit default text box
            emacs.edit_default_text_box()


        # FINALLY: get cmd from cmdline
        cmd = emacs.get_cmd()
        # if no cmd entered, edit text box
        if len(cmd) == 0:
            emacs.edit_default_text_box()
        ### end of program while loop ###


    # outside of while loop: end the program
    curses.endwin()
    return
    ### END OF MAIN PROGRAM ###


# entry point for main program, if error, no problem just exit
if __name__ == '__main__':
    wrapper(main)
