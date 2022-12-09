#!/usr/bin/env python3

from string import printable
from io import TextIOBase

from rich import print

from textual.app import App, ComposeResult
from textual.containers import Container, Content
from textual.widgets import Label
from textual import events

class Text_Field(Content):

    valid_chars = printable.split()[0] + ' '

    def __init__(self):
        super().__init__()
        self.text = ""
        self.cmd = ""
        self.cursor_idx = 1
        self.writer = TextIOBase()

    def write(self, text=""):
        self.text = self.text[:self.cursor_idx] + text + self.text[self.cursor_idx:]
        self.cmd += self.cmd[:self.cursor_idx] + text + self.cmd[self.cursor_idx:]
        self.cursor_idx += 1
        self.refresh()

    def back(self):
        self.cursor_idx -= 1
        self.text = self.text[:self.cursor_idx] + self.text[self.cursor_idx:]
        self.cmd = self.cmd[:self.cursor_idx] + self.cmd[self.cursor_idx:]
        self.refresh()

    def render(self):
        return self.text

    def on_mount(self):
        self.writer.write = self.write
        self.writer.write('> ')
        self.cmd = ""
        self.focus()

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
            if self.cursor_idx != 2:
                self.cursor_idx -= 1
        elif event_key == 'right':
            if self.cursor_idx != len(self.text):
                self.cursor_idx += 1
        elif event_key == 'up':
            self.cursor_idx = 2
        elif event_key == 'down':
            self.cursor_idx = len(self.text)
        elif event_char in self.valid_chars and event_char != '|':
            self.writer.write(event_char)
        elif event_char == '\r':
            self.styles.height = self.styles.height[0] + 1
            self.writer.write('\n')
            try:
                self.writer.write(str(eval(self.cmd)))
                newline = True
            except:
                newline = False
            if newline:
                self.writer.write('\n')
            self.writer.write('[white]> ')
            self.cmd = ""
            self.cursor_idx = 1


class Window(Container):

    def __init__(self):
        super().__init__()
        self.text_field = Text_Field()
        self.label = Label("Terminal")
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))

    def compose(self) -> ComposeResult:
        yield self.label
        yield self.text_field

    def on_mouse_down(self, event: events.MouseDown):
        for window in app.windows:
            window.styles.layer = 'below'
        self.styles.layer = 'above'
        self.x = int(str(self.styles.offset[0]))
        self.y = int(str(self.styles.offset[1]))
        self.text_field.focus()

    def on_mouse_up(self, event: events.MouseUp):
        self.styles.offset = (event.screen_x-self.x,event.screen_y-self.y)



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
            content-align: center middle;
        }
        Label {
            content-align: center top;
        }
        Text_Field {
            content-align: left top;
            width: 100%;
            height: 10;
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
