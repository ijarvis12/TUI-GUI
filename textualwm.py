#!/usr/bin/env python3

from textual.app import App
from textual.widgets import TextLog
from textual import events

import os

class Window(TextLog):

    def __init__(self):
        super().__init__()
        self.border_title = "Terminal"
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))
        self.border_subtitle = self.cmd = ""

    def on_mouse_down(self, event: events.MouseDown):
        for window in app.windows:
            window.styles.layer = 'below'
        self.styles.layer = 'above'
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))
        self.focus()

    def on_mouse_up(self, event: events.MouseUp):
        self.styles.offset = (event.screen_x-self.x, event.screen_y-self.y)

    def on_mount(self):
        self.cmd = ""
        self.border_subtitle = '> '
        self.focus()

    def on_key(self, event: events.Key):
        event_char = event.character
        event_key = event.key
        if event_key == 'home':
            app.add_window()
        elif event_key == 'end':
            app.remove_window()
        elif event_char is None:
            pass
        elif event_key == 'backspace' or event_key == 'delete':
            if len(self.cmd) > 0:
                self.border_subtitle = self.border_subtitle[:-1]
                self.cmd = self.cmd[:-1]
        elif event_char == '\r':
            self.write(self.cmd)
            try:
                output = eval(self.cmd)
                self.write(output)
            except:
                pass
            self.cmd = ""
            self.border_subtitle = '> '
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
            layers: below above;
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

    windows = []

    def on_key(self, event: events.Key):
        if event.key == 'home':
            self.add_window()
        elif event.key == 'end':
            self.remove_window()

    def add_window(self):
        for window in self.windows:
            window.styles.layer = 'below'
        new_window = Window()
        self.windows.append(new_window)
        new_window.styles.layer = 'above'
        self.mount(new_window)

    def remove_window(self):
        if len(self.windows) > 0:
            self.windows[-1].remove()
            self.windows = self.windows[:-1]


if __name__ == "__main__":
    cd = os.chdir
    ls = os.listdir
    pwd = os.getcwd
    app = WindowManager()
    app.run()
