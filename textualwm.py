#!/usr/bin/env python3

from string import printable
from time import sleep
from io import TextIOBase

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
        self.writer = TextIOBase()
        self.h = 10

    def write(self, text=""):
        self.text += text
        self.cmd += text
        self.refresh()

    def render(self):
        return self.text

    def on_mount(self):
        self.focus()
        self.writer.write = self.write
        self.writer.write('> ')
        self.cmd = ""

    def on_click(self, event: events.Click):
        self.focus()

    def on_key(self, event: events.Key):
        event_char = event.char
        if event.key == 'home':
            app.add_window()
        elif event.key == 'end':
            app.remove_window()
        elif event_char in self.valid_chars:
            self.writer.write(event_char)
        elif event_char == '\r':
            self.h += 1
            self.styles.height = self.h
            self.writer.write('\n')
            try:
                self.writer.write(str(eval(self.cmd)))
                newline = True
            except:
                newline = False
            if newline:
                self.writer.write('\n')
            self.writer.write('> ')
            self.cmd = ""


class Window(Container):

    def compose(self) -> ComposeResult:
        yield Label("Terminal")
        yield Text_Field()

    def on_focus(self):
        self.focus(False)

    def on_mouse_down(self, event: events.MouseDown):
        for window in app.windows:
            window.styles.layer = 'below'
        self.styles.layer = 'above'
        while sleep(0.1):
            self.styles.offset = (event.screen_x, event.screen_y)


class WindowManager(App):
    CSS = """
        Screen {
            layout: grid;
            grid-size: 1280 720;
            align: left top;
            max-height: 100%;
            max-width: 100%;
            overflow: hidden;
            layers: below above;
        }
        Window {
            column-span: 500;
            row-span: 300;
            border: white round;
            content-align: center middle;
        }
        Label {
            content-align: center top;
            width: 100%;
        }
        Vertical {
            overflow-y: scroll;
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
