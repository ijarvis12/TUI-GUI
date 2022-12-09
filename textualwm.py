#!/usr/bin/env python3

from string import printable
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
        self.writer.write = self.write
        self.writer.write('> ')
        self.cmd = ""

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

    def __init__(self):
        super().__init__()
        self.text_field = Text_Field()
        self.label = Label("Terminal")

    def compose(self) -> ComposeResult:
        yield self.label
        yield self.text_field

    def on_mouse_down(self, event: events.MouseDown):
        for window in app.windows:
            window.styles.layer = 'below'
        self.styles.layer = 'above'
        self.styles.offset = (event.screen_x-event.x,event.screen_y-event.y)
        self.text_field.focus()


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
