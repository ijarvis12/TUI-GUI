#!/usr/bin/env python3

from string import printable
from io import TextIOBase

from rich import print

from textual.app import App, ComposeResult
from textual.containers import Content
from textual.widgets import Label
from textual import events


class Window(Content):

    allow_vertical_scroll = True
    valid_chars = printable.split()[0] + ' '

    def __init__(self):
        super().__init__()
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))
        self.text = ""
        self.cmd = ""
        self.cursor_idx = 0
        self.writer = TextIOBase()

    def compose(self) -> ComposeResult:
        yield Label("Terminal")

    def on_mouse_down(self, event: events.MouseDown):
        for window in app.windows:
            window.styles.layer = 'below'
        self.styles.layer = 'above'
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))
        self.focus()

    def on_mouse_up(self, event: events.MouseUp):
        self.styles.offset = (event.screen_x-self.x,event.screen_y-self.y)
  
    def write(self, text=""):
        if self.text != '\n':
            self.cursor_idx += 1
            self.text = self.text.replace('|','')
            self.text = self.text[:self.cursor_idx] + text + '|' + self.text[self.cursor_idx:]
            self.cmd = self.cmd[:self.cursor_idx] + text + self.cmd[self.cursor_idx:]
            self.refresh()
        else:
            self.text = self.text.replace('|','')
            self.text += '\n'
            self.cursor_idx = len(self.text)
            self.refresh()

    def render(self):
        return self.text

    def on_mount(self):
        self.writer.write = self.write
        self.writer.write('\n[white]> ')
        self.cmd = ""
        self.cursor_idx = len(self.text)
        self.focus()

    def back(self):
        if self.cursor_idx > 8:
            self.cursor_idx -= 1
            self.text = self.text.replace('|','')
            self.text = self.text[:self.cursor_idx+1] + '|' + self.text[self.cursor_idx+2:]
            self.cmd = self.cmd[:self.cursor_idx+1] + self.cmd[self.cursor_idx+2:]
            self.refresh()

    def left(self):
        if self.cursor_idx > 8:
            self.text = self.text.replace('|','')
            self.text = self.text[:self.cursor_idx-1] + '|' + self.text[self.cursor_idx-1:]
            self.cursor_idx -= 1
            self.refresh()

    def right(self):
        if self.cursor_idx < len(self.text):
            self.text = self.text.replace('|','')
            self.text = self.text[:self.cursor_idx+2] + '|' + self.text[self.cursor_idx+2:]
            self.cursor_idx += 1
            self.refresh()

    def on_key(self, event: events.Key):
        event_char = event.char
        event_key = event.key
        if event_key == 'home':
            app.add_window()
        elif event_key == 'end':
            app.remove_window()
        elif event_key == 'backspace' or event_key == 'delete':
            self.back()
        elif event_key == 'left':
            self.left()
        elif event_key == 'right':
            self.right()
        elif event_char is None:
            pass
        elif event_char in self.valid_chars and event_char != '|':
            self.writer.write(event_char)
        elif event_char == '\r':
            #self.styles.height = self.styles.height[0] + 1
            self.writer.write('\n')
            self.refresh()
            try:
                self.writer.write(str(eval(self.cmd)))
                newline = True
            except:
                newline = False
            if newline:
                self.writer.write('\n')
            self.writer.write('[white]> ')
            self.cmd = ""
            self.cursor_idx = len(self.text)



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
            height: 25;
            width: 82;
            border: white round;
            content-align: left top;
            scrollbar-gutter: stable;
            scrollbar-size-vertical: 1;
        }
        Label {
            content-align: center top;
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
    app = WindowManager()
    app.run()
