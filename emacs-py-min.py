#!/usr/bin/env python3

import curses
from curses import wrapper, window, A_REVERSE, A_NORMAL
from curses.textpad import Textbox

from time import sleep


class ScrollTextbox():
    """Editing widget using the interior of a window object.
     Supports the following Emacs-like key bindings:

    Ctrl-A      Go to left edge of window.
    Ctrl-B      Cursor left, wrapping to previous line if appropriate.
    Ctrl-D      Delete character under cursor.
    Ctrl-E      Go to right edge.
    Ctrl-F      Cursor right, wrapping to next line when appropriate.
    Ctrl-G      Terminate, returning the window contents.
    Ctrl-H      Delete character backward.
    Ctrl-J      Terminate if the window is 1 line, otherwise insert newline.
    Ctrl-K      If line is blank, delete it, otherwise clear to end of line.
    Ctrl-L      Refresh screen.
    Ctrl-N      Cursor down; move down one line.
    Ctrl-O      Insert a blank line at cursor location.
    Ctrl-P      Cursor up; move up one line.

    Move operations do nothing if the cursor is at an edge where the movement
    is not possible.  The following synonyms are supported where possible:

    KEY_LEFT = Ctrl-B,
    KEY_RIGHT = Ctrl-F,
    KEY_UP = Ctrl-P,
    KEY_DOWN = Ctrl-N,
    KEY_BACKSPACE = Ctrl-H
    """

    def __init__(self, win):
        """Initialize the object"""
        self.win = win
        win.keypad(1)
        self.win.idlok(True)
        self.win.scrollok(True)
        self.stripspaces = True
        self.line_num = 0
        self.top_line_num = 0
        self.x_indx = [1]
        self.text = [""]
        self.save_needed = False
        self._update_max_yx()

    def toggle_save_needed(self, bool):
        """Set save_needed bool"""
        self.save_needed = bool
        # return nothing
        return

    def _update_max_yx(self):
        """Update object's window dimensions"""
        maxy, maxx = self.win.getmaxyx()
        self.maxy = maxy - 1
        self.maxx = maxx - 1

    def _end_of_line(self, y):
        """Go to the location of the first blank on the given line,
        returning the index of the last non-blank character."""
        self._update_max_yx()
        last = self.maxx
        while True:
            if curses.ascii.ascii(self.win.inch(y, last)) != curses.ascii.SP:
                last = min(self.maxx, last+1)
                break
            elif last == 0:
                break
            last = last - 1
        return last

    def _insert_printable_char(self, ch):
        """Insert a printable character into the window"""
        self._update_max_yx()
        (y, x) = self.win.getyx()
        try:
            self.win.addch(ch)
        except curses.error:
            pass
        (y, x) = self.win.getyx()
        # return nothing
        return

    def _toggle_brackets(self, cmd="", bracket=""):
        """Toggle the brackets at each end of the window"""
        if len(cmd) == 0 or cmd == "normal":
            if bracket == ">":
                self.win.addch(self.win.getyx()[0], self.maxx, ' ', A_NORMAL)
            elif bracket == "<":
                self.win.addch(self.win.getyx()[0], 0, ' ', A_NORMAL)
        elif cmd == "reverse":
            if bracket == ">":
                self.win.addch(self.win.getyx()[0], self.maxx, '>', A_REVERSE)
            if bracket == "<":
                self.win.addch(self.win.getyx()[0], 0, '<', A_REVERSE)
        # return nothing
        return


    # overwrite Textbox do_command for scrolling
    def do_command(self, ch):
        """Process a single editing command."""
        self._update_max_yx()
        (y, x) = self.win.getyx()

        # print character
        if curses.ascii.isprint(ch):
            self.toggle_save_needed(True)
            if self.line_num > len(self.text) - 1:
                for line_num in range(len(self.text),self.line_num+1):
                    self.text.append("")
                    self.x_indx.append(1)
            if x > len(self.text[self.line_num]) - 1:
                self.text[self.line_num] += " " * (x - len(self.text[self.line_num]))
            if x == self.maxx:
                self.x_indx[self.line_num] += 1
                self._toggle_brackets("reverse", "<")
                self.win.addstr(y, 1, self.text[self.line_num][self.x_indx[self.line_num]*self.maxx:])
                if len(self.text[self.line_num]) > (self.x_indx[self.line_num]*self.maxx + self.maxx - 1):
                    self._toggle_brackets("reverse", ">")
                self.win.move(y, 1)
            self._insert_printable_char(ch)
            x_coord = self.x_indx[self.line_num]*self.maxx
            self.text[self.line_num] = self.text[self.line_num][:x_coord+x] + chr(ch) + self.text[self.line_num][x_coord+x+1:]

        # Ctrl-a (Go to left edge of window)
        elif ch == curses.ascii.SOH:                           # ^a
            self.x_indx[self.line_num] = 1
            self.win.move(y, 0)
            self.win.addstr(self.text[self.line_num])
            if len(self.text[self.line_num]) > self.maxx:
                self._toggle_brackets("reverse", ">")

        # Ctrl-b (Cursor left, wrapping to previous line if appropriate (backspace doesn't work))
        elif ch in (curses.ascii.STX, curses.KEY_LEFT, curses.ascii.BS, curses.KEY_BACKSPACE):     # ^b
            if x > 0 and self.x_indx[self.line_num] == 1:
                self.win.move(y, x-1)
            elif self.x_indx[self.line_num] > 1:
                if x > 1:
                    self.win.move(y, x-1)
                else:
                    self.x_indx[self.line_num] -= 1
                    x_coord = (self.x_indx[self.line_num]-1)*self.maxx
                    self.win.addstr(y, 0, self.text[self.line_num][x_coord:])
                    if len(self.text[self.line_num]) > (self.maxx - 1):
                        self._toggle_brackets("reverse", ">")
                        self.win.move(y, self.maxx-1)
                    else:
                        self.win.move(y, self.maxx)
                    if self.x_indx[self.line_num] > 1:
                        self._toggle_brackets("reverse", "<")
            elif y == 0:
                if self.line_num > 0:
                    self.win.scroll(-1)
                    self.line_num -= 1
                    self.top_line_num -= 1
                    self.win.move(y, 0)
                    self.win.addstr(self.text[self.line_num])
                    if len(self.text[self.line_num]) > (self.maxx - 1):
                        self._toggle_brackets("reverse", ">")
                        self.win.move(y, self.maxx-1)
                    else:
                        self.win.move(y, len(self.text[self.line_num]))
            #elif self.stripspaces:
            #    self.win.move(y-1, self._end_of_line(y-1))
            #    self.line_num -= 1
            else:
                self.win.move(y-1, 0)
                self.line_num -= 1
            if ch in (curses.ascii.BS, curses.KEY_BACKSPACE):
                self.win.delch()
                x_coord = (self.x_indx[self.line_num]-1)*self.maxx+x
                self.text[self.line_num] = self.text[self.line_num][:x_coord] + self.text[self.line_num][x_coord+1:]

        # Ctrl-d (Delete character under cursor)
        elif ch == curses.ascii.EOT:                           # ^d
            self.toggle_save_needed(True)
            self.win.delch()
            x_coord = (self.x_indx[self.line_num]-1)*self.maxx+x
            self.text[self.line_num] = self.text[self.line_num][:x_coord] + self.text[self.line_num][x_coord+1:]
            if len(self.text[self.line_num][x_coord:]) < self.maxx:
                self._toggle_brackets("normal", ">")

        # Ctrl-e (Go to right edge)
        elif ch == curses.ascii.ENQ:                           # ^e
            if len(self.text[self.line_num]) < self.x_indx[self.line_num]*self.maxx:
                self.win.move(y, len(self.text[self.line_num]))
            else:
                self.win.move(y, self.maxx)

        # Ctrl-f (Cursor right, wrapping to next line when appropriate)
        elif ch in (curses.ascii.ACK, curses.KEY_RIGHT):       # ^f
            if x == self.maxx-1 and len(self.text[self.line_num]) > self.x_indx[self.line_num]*self.maxx:
                x_coord = self.x_indx[self.line_num]*self.maxx
                self.win.addstr(y, 1, self.text[self.line_num][x_coord:])
                self.win._toggle_brackets("reverse", "<")
            elif x < self.maxx:
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

        # Ctrl-g (Terminate, returning the window contents)
        elif ch == curses.ascii.BEL:                           # ^g
            return 0           # return zero

        # Ctrl-j (Terminate if the window is 1 line, otherwise insert newline)
        elif ch == curses.ascii.NL:                            # ^j
            if self.maxy == 0:
                return 0       # return zero
            self.toggle_save_needed(True)
            if y == self.maxy:
                self.win.scroll(1)
                self.top_line_num += 1
                self.win.move(y, 0)
            else:
                self.win.move(y+1, 0)
            self.win.insertln()
            self.line_num += 1
            self.text = self.text[:self.line_num] + [""] + self.text[self.line_num:]
            self.x_indx = self.x_indx[:self.line_num] + [1] + self.x_indx[self.line_num:]
            if self.line_num > len(self.text) - 1:
                self.text.append("")
                self.x_indx.append(1)

        # Ctrl-k (If line is blank, delete it, otherwise clear to end of line)
        elif ch == curses.ascii.VT:                            # ^k
            self.toggle_save_needed(True)
            if x == 0 and self._end_of_line(y) == 0:
                self.win.deleteln()
            else:
                # first undo the effect of self._end_of_line
                self.win.move(y, x)
                self.win.clrtoeol()
            self.text[self.line_num] = ""
            self.x_indx[self.line_num] = 1

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
                    self.toggle_save_needed(True)
                    self.text.append("")
                    self.x_indx.append(1)
                self.win.move(y, x)
            else:
                self.win.move(y+1, x)
                self.line_num += 1
                # sanity check #
                if self.line_num > len(self.text) - 1:
                    for i in range(len(self.text),self.line_num+1):
                        self.text.append("")
                        self.x_indx.append(1)
                # end sanity check #
            if x > len(self.text[self.line_num]):
                self.win.move(y+1, len(self.text[self.line_num]))

        # Ctrl-o (Insert a blank line at cursor location)
        elif ch == curses.ascii.SI:                            # ^o
            self.toggle_save_needed(True)
            self.win.insertln()
            if self.line_num > 0:
                self.text = self.text[:self.line_num] + [""] + self.text[self.line_num:]
                self.x_indx = self.x_indx[:self.line_num] + [1] + self.x_indx[sefl.line_num:]
            else:
                self.text = [""] + self.text
                self.x_indx = [1] + self.x_indx
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


    def edit(self, stdscr, buffer_num):
        """Edit in the widget window"""
        while 1:
            ch = self.win.getch()
            if not ch:
                continue
            if not self.do_command(ch):
                break
            # update statusline (y, x)
            s_maxy, s_maxx = stdscr.getmaxyx()
            # statuline string
            statusline = '### Buffer '+ str(buffer_num) + ' ' + '# Row ' + str(self.line_num) + ' Col ' + str(self.win.getyx()[1]) + ' '
            # redraw bottom hline (statusline)
            stdscr.insstr(s_maxy-2, 0, statusline)
            stdscr.hline(s_maxy-2, len(statusline) , '#', s_maxx-len(statusline))
            stdscr.refresh()
            # need to refresh win after screen for cursor to appear in win
            self.win.refresh()
        # return nothing
        return


class Buffer():
    def __init__(self, stdscr):
        """Create new buffer for editing"""
        # get screen dimensions
        maxy, maxx = stdscr.getmaxyx()
        # setup text box
        win = stdscr.subwin(maxy-2, maxx, 0, 0)
        self.text_box = ScrollTextbox(win)


class Buffers():
    def __init__(self, stdscr):
        """Initialize the Application"""
        ### start of buffers setup ###
        self.screen = stdscr
        self.screen.clear()
        maxy, maxx = self.screen.getmaxyx()
        # setup cmdline
        cmdline = stdscr.subwin(1, maxx, maxy-1, 0)
        cmdline.idcok(True)
        self.cmd_box = Textbox(cmdline)
        self.cmd_box.stripspaces = True
        self.cmd = 'edit'
        # initialize first buffer
        self.buffers = [Buffer(self.screen)]
        self.buffer_num = 0
        self.current_buffer = self.buffers[0]
        # update the buffer
        self.update_buffer()
        self.update_statusline("Help buffer: 'Ctrl-G'+'h'+<Enter>")
        ### end buffers setup ###

    def add_buffer(self):
        """Add a buffer"""
        self.buffers.append(Buffer(self.screen))
        self.buffer_num = len(self.buffers) - 1
        self.current_buffer = self.buffers[-1]
        # return nothing
        return

    def get_cmd(self):
        """Get a command from commandline"""
        self.cmd_box.win.clear()
        self.cmd_box.win.refresh()
        self.cmd = self.cmd_box.edit().strip(' ').lower()
        # return nothing
        return

    def update_statusline(self, status):
        """Update the statusline"""
        t_box = self.current_buffer.text_box
        s_maxy, s_maxx = self.screen.getmaxyx()
        # statuline string
        if len(status) > 0:
            statusline = '### ' + status + ' '
        else:
            statusline = '### Buffer '+ str(self.buffer_num) + ' ' + '# Row ' + str(t_box.line_num) + ' Col ' + str(t_box.win.getyx()[1]) + ' '
        # redraw bottom hline (statusline)
        self.screen.insstr(s_maxy-2, 0, statusline)
        self.screen.hline(s_maxy-2, len(statusline) , '#', s_maxx-len(statusline))
        self.screen.refresh()

        # return nothing
        return

    def update_text(self):
        """Redisplay text box text"""
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
            y = t_box.win.getyx()[0]
            t_box.win.insnstr(line, maxx)
            if len(line) > maxx:
                t_box.win.insch(y, maxx, '>', A_REVERSE)
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
        """Redraw the buffer"""
        if buffer_num > -1: # if buffer number is not -1, update the buffer number and current buffer
            # Update the buffer number
            self.buffer_num = buffer_num
            self.current_buffer = self.buffers[buffer_num]
        self.screen.clear()
        # redisplay text
        self.update_text()
        # update statusline
        self.update_statusline("")
        # return nothing
        return

    def edit_default_text_box(self):
        """Edit default text box"""
        text_box = self.current_buffer.text_box
        # move cursor to top left corner
        text_box.line_num = text_box.top_line_num
        text_box.win.move(0, 0)
        self.update_statusline("")
        # edit text box
        return text_box.edit(self.screen, self.buffer_num)

    def del_buffer(self):
        """Delete current buffer and update buffer number (and current buffer)"""
        # remove buffer and associated objects
        self.screen.clear()
        self.screen.refresh()
        del self.buffers[self.buffer_num]
        # update buffer number (and buffer)
        if self.buffer_num > 0:
            self.update_buffer(self.buffer_num - 1)
        else:
            self.update_buffer(0)
        # return nothing
        return

    def remove_buffer(self):
        """Remove current buffer to have one less buffer"""
        # if the buffer has unsaved work, ask about removing
        if self.current_buffer.text_box.save_needed:
            self.update_statusline('Unsaved work. Remove buffer [y/N]?')
            # get user's choice
            self.get_cmd()
            if 'y' in self.cmd: # if user entered yes, remove buffer
                self.del_buffer()
        else: # else buffer has no unsaved work, safe to remove
            self.del_buffer()
        # return nothing
        return

    def maybe_quit(self):
        """If a save is needed, save then quit"""
        # Check for unsaved work, and ask
        for b,buff in enumerate(self.buffers):
            if buff.text_box.save_needed:
                self.update_buffer(b)
                self.update_statusline('Unsaved work. Quit [y/N]?')
                # get user's choice
                self.get_cmd()
                if 'n' in self.cmd: # if user entered no, edit text box
                    self.cmd = "edit"
                # break out of for loop no matter the choice
                break
        # return nothing
        return

    def mainloop(self):
        """Main program loop"""
        # while cmd is not 'quit' execute while loop
        while self.cmd != 'q' and self.cmd != 'quit' and self.cmd != 'exit':
            # get info
            buffer = self.current_buffer
            t_box = buffer.text_box


            # COMMAND: help buffer display
            if self.cmd == 'h' or self.cmd == 'help':
                self.add_buffer()
                # update buffer
                self.update_buffer()
                # set text box help text
                t_box = self.current_buffer.text_box
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
"'o[pen buffers]' = list open buffers in new buffer"]
                # display help text
                self.update_buffer()
                # edit the text box
                self.edit_default_text_box()


            # COMMAND: open buffer with numbered open buffers
            elif self.cmd == 'o' or self.cmd == 'open buffers':
                self.add_buffer()
                # update buffer
                self.update_buffer()
                # set text box header text
                t_box = self.current_buffer.text_box
                t_box.text = [
"==========  Open buffer Buffers  ==========",
" Warning: This buffer will not auto update ",
"      Recommended to remove when done      ",
"==========================================="]
                # get open buffers
                for b,buff in enumerate(self.buffers):
                    if b == len(self.buffers) - 1:
                        t_box.text.append("* Buffer "+str(b)+" * (Current Buffer)")
                    else:
                        t_box.text.append("  Buffer "+str(b))
                # display text box text
                self.update_buffer()
                # edit the text box
                self.edit_default_text_box()


            # COMMAND: edit text box
            elif self.cmd == 'e' or self.cmd == 'edit':
                self.edit_default_text_box()


            # COMMAND: new buffer
            elif self.cmd == 'n' or self.cmd == 'new' or self.cmd =='new buffer':
                self.add_buffer()
                # update buffer
                self.update_buffer()
                # edit default text box
                self.edit_default_text_box()


            # COMMAND: remove buffer
            elif self.cmd == 'r' or self.cmd == 'remove' or self.cmd == 'remove buffer':
                # if more than one buffer left, remove
                if len(self.buffers) > 1:
                    self.remove_buffer()
                    self.edit_default_text_box()
                else: # else break out of while loop to save and quit, or not
                    break


            # COMMAND: next buffer
            elif self.cmd == 'b' or self.cmd == 'buffer':
                # set buffer number
                if self.buffer_num < len(self.buffers) - 1:
                    self.update_buffer(self.buffer_num + 1)
                else:
                    self.update_buffer(0)
                # edit default text box
                self.edit_default_text_box()


            # COMMAND: save to file
            elif self.cmd == 'fs' or self.cmd == 'file save' or self.cmd == 'file save as':
                # update statusline
                self.update_statusline('Filename To Save As: ')
                # get filename
                self.get_cmd()
                filename = self.cmd

                # update statusline
                self.update_statusline('Saving File...')
                # get text for saving
                text_to_save = ""
                for line_of_text in t_box.text:
                    text_to_save += line_of_text + '\n'

                # try to save file
                try:
                    with open(filename, 'w') as file:
                        file.write(text_to_save)
                    # update statusline if successful
                    self.update_statusline('Save Successful')
                    # No save needed anymore, at least until another edit
                    buffer.text_box.toggle_save_needed(False)
                    # pause for a tiny bit to show the updated statusline before updating again
                    sleep(.1)
                    # update statusline
                    self.update_statusline("")
                except: # update statusline if failed
                    self.update_statusline('Error: File Save Failed')

                # free up var for memory (could be large file)
                del text_to_save

                # edit default text box with updated statusline
                self.edit_default_text_box()


            # COMMAND: open file
            elif self.cmd == 'fo' or self.cmd == 'file open':
                # update statusline
                self.update_statusline('File To Open: ')
                # get filename
                self.get_cmd()
                filename = self.cmd

                # var to hold text
                text_from_file = ""
                # try to open file
                try:
                    with open(filename, 'r') as file:
                        text_from_file = file.readlines()
                except: # update statusline if failed
                    self.update_statusline('Error: File Open Failed')

                # if any text read from file, add to buffer
                if len(text_from_file) > 0:
                    t_box.text = []
                    for line in text_from_file:
                        t_box.text.append(line.strip('\n'))

                    # free up var for memory (could be large file)
                    del text_from_file

                    # update buffer for displaying the text
                    self.current_buffer.text_box.line_num = 0
                    self.current_buffer.text_box.top_line_num = 0
                    self.update_buffer()

                # edit default text box
                self.edit_default_text_box()


            # FINALLY: get cmd from cmdline
            self.get_cmd()
            # if no cmd entered, edit text box
            if len(self.cmd) == 0:
                self.edit_default_text_box()
            ### end of program while loop ###


        # check for unsaved work, and possibly quit
        self.maybe_quit()
        # if need to save, enter mainloop
        if "edit" in self.cmd:
            self.mainloop()
        # return nothing
        return


def main(stdscr):
    """The Main Program"""
    ### Initialize Emacs ###
    emacs = Buffers(stdscr)
    ### MAIN PROGRAM ###
    emacs.mainloop()
    ### END OF MAIN PROGRAM ###
    curses.endwin()
    return


# entry point for main program, if error, no problem just exit
if __name__ == '__main__':
    wrapper(main)
