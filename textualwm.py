#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.widgets import TextLog
from textual import events

import os, socket
import pwd as _pwd

class Window(TextLog):

    PS1 = _pwd.getpwuid(os.geteuid())[0] + '@' + socket.gethostname() + ' >>> '

    def __init__(self):
        super().__init__(markup=True)
        self.border_title = "Terminal"
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))
        self.border_subtitle = self.cmd = ""

    def on_mouse_down(self, event: events.MouseDown):
        if self != app.windows['above']:
            # temp window is former 'above'
            temp_win = app.windows['above']
            temp_win.styles.layer = 'temp'
            # 'above' window becomes this one (self)
            prev_layer = self.styles.layer
            app.windows['above'] = self
            app.windows['above'].styles.layer = 'above'
            # temp window places into previous self window layer
            app.windows[prev_layer] = temp_win
            app.windows[prev_layer].styles.layer = prev_layer
            del temp_win
        # self window placement info recording and focus
        self.x = event.screen_x
        self.y = event.screen_y
        self.focus()

    def on_mouse_up(self, event: events.MouseUp):
        old_x = self.x
        old_y = self.y
        new_x = event.screen_x
        new_y = event.screen_y
        cmp_x = new_x > self.x
        cmp_y = new_y > self.y
        self.styles.offset = ((cmp_x * new_x + cmp_x * old_x + (not cmp_x) * old_x - (not cmp_x) * new_x) // 2,
                              (cmp_y * new_y + cmp_y * old_y + (not cmp_y) * old_y - (not cmp_y) * new_y) // 2,)
        self.focus()

    def on_mount(self):
        self.cmd = ""
        self.border_subtitle = self.PS1
        self.focus()

    def on_key(self, event: events.Key):
        event_char = event.character
        event_key = event.key
        if event_char is None:
            pass
        elif event_key == 'backspace' or event_key == 'delete':
            if len(self.cmd) > 0:
                self.border_subtitle = self.border_subtitle[:-1]
                self.cmd = self.cmd[:-1]
        elif event_key == 'ctrl+d':
            app.remove_window()
        elif event_key == 'ctrl+l':
            self.clear()
            self.cmd = ""
            self.border_subtitle = self.PS1
        elif event_char == '\r':
            self.write(self.cmd)
            try:
                output = eval(self.cmd)
                self.write(output)
            except:
                pass
            self.cmd = ""
            self.border_subtitle = self.PS1
        else:
            self.border_subtitle += event_char
            self.cmd += event_char



class WindowManager(App):
    CSS = """
        Screen {
            align: left top;
            max-height: 100%;
            max-width: 100%;
            overflow: hidden;
            layers: temp below below1 below2 below3 below4 below5 below6 below7 below8 above;
        }
        Window {
            height: 20;
            width: 40;
            border: white round;
            content-align: left top;
            scrollbar-gutter: stable;
            scrollbar-size-vertical: 1;
        }
    """

    windows = {}

    def on_key(self, event: events.Key):
        if event.key == 'home':
            self.add_window()
        elif event.key == 'end':
            self.remove_window()

    def add_window(self):
        if len(self.windows) < 8:
            if len(self.windows) > 0:
                # old window, new below name/layer
                b_len_str = 'below' + str(len(self.windows))
                # old window
                temp_win = self.windows['above']
                self.windows[b_len_str] = temp_win
                self.windows[b_len_str].styles.layer = b_len_str
                del self.windows['above']
                del temp_win
            # new window
            self.windows['above'] = Window()
            self.windows['above'].styles.layer = 'above'
            if len(self.windows) > 1:
                self.windows['above'].styles.offset = (int(str(self.windows[b_len_str].styles.offset[0])) + 2,
                                                       int(str(self.windows[b_len_str].styles.offset[1])) + 2)
            self.mount(self.windows['above'])

    def remove_window(self):
        # remove 'above' window
        if len(self.windows) > 0:
            self.windows['above'].remove()
            del self.windows['above']
            # make last window in dict 'above'
            if len(self.windows) > 0:
                temp_win = self.windows[list(self.windows)[-1]]
                del self.windows[list(self.windows)[-1]]
                self.windows['above'] = temp_win
                self.windows['above'].styles.layer = 'above'
                del temp_win


if __name__ == "__main__":
    cd = os.chdir
    ls = os.listdir
    pwd = os.getcwd
    whoami = lambda: _pwd.getpwuid(os.geteuid())[0]
    app = WindowManager()
    app.run()
