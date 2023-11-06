#!/usr/bin/env python3

from functools import partial

from textual import on
from textual.app import App, ComposeResult
from textual.command import Hit, Hits, Provider
from textual.widgets import Header, DirectoryTree
from textual_terminal import Terminal
from textual import events

from PIL import Image
from textual_imageview.viewer import ImageViewer

class Term(Terminal):

    def __init__(self, command):
        super().__init__(command, default_colors="textual")
        self.x = self.styles.offset[0]
        self.y = self.styles.offset[1]

    def on_mount(self):
        self.start()
        self.focus()

    def on_mouse_down(self, event: events.MouseDown):
        if self != app.windows['above']:
            # temp window is former 'above'
            temp_win = app.windows['above']
            temp_win.styles.layer = 'temp'
            # clicked window becomes 'above', and save previous layer
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
        cmp_x = new_x > old_x
        cmp_y = new_y > old_y
        self.styles.offset = ((cmp_x * new_x + cmp_x * old_x + (not cmp_x) * old_x - (not cmp_x) * new_x) // 2,
                              (cmp_y * new_y + cmp_y * old_y + (not cmp_y) * old_y - (not cmp_y) * new_y) // 2,)
        self.focus()

    def on_key(self, event: events.Key):
        if event.key == 'home':
            app.add_window()
        elif event.key == 'end':
            app.remove_window()


class DECommands(Provider):
    """A command provider to open/close terminals and set the wallpaper"""

    commands = ["New Terminal", "Remove Terminal", "Set Wallpaper"]
    command = ""

    async def assign_command(self, command: str):
        self.command = command

    async def search(self, query: str) -> Hits:
        """Search for command hits"""
        self.command = ""
        matcher = self.matcher(query)
        for c in self.commands:
            score = matcher.match(c)
            if score > 0:
                yield Hit(score, matcher.highlight(c), partial(self.assign_command, c), help="Desktop Environment Command")

    async def shutdown(self):
        comm = self.command
        if len(comm) > 0:
            if comm == "New Terminal":
                self.app.add_window()
            elif comm == "Remove Terminal":
                self.app.remove_window()
            elif comm == "Set Wallpaper":
                self.app.mount(DirectoryTree('./'))



class DesktopEnvironment(App):
    CSS = """
        Screen {
            align: left top;
            max-height: 100%;
            max-width: 100%;
            overflow: hidden;
            layers: temp wallpaper below below1 below2 below3 below4 below5 below6 below7 below8 above header;
        }
        Header {
            layer: header;
        }
        ImageViwer {
            min-height: 100%;
            min-width: 100%;
            layer: wallpaper;
        }
        Term {
            max-height: 20;
            max-width: 80;
            border: white round;
            offset: 2 2;
        }
        DirectoryTree {
            offset: 2 2;
            layer: header;
        }
    """

    COMMANDS = App.COMMANDS | {DECommands}

    windows = {}

    def __init__(self):
        """Inits background image and panel"""
        super().__init__()
        self.header = Header(show_clock=True)
        self.title = "Textual Desktop Environment"
        self.sub_title = "By Ian P. Jarvis"
        self.image_path = "./thunderstorm.jpg"
        try:
            self.image = Image.open(self.image_path)
            self.image_viewer = ImageViewer(self.image)
        except:
            print(f"{self.image_path} does not exist.")
            exit()

    def compose(self) -> ComposeResult:
        yield self.header
        yield self.image_viewer

    @on(DirectoryTree.FileSelected)
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.image_path = event.path
        try:
            self.image = Image.open(self.image_path)
            self.image_viewer.remove()
            self.image_viewer = ImageViewer(self.image)
            self.mount(self.image_viewer)
        except:
            pass
        finally:
            self.query_one(DirectoryTree).remove()

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
            self.windows['above'] = Term(command="bash")
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
    app = DesktopEnvironment()
    app.run()
