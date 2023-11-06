#!/usr/bin/env python3

import sys

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import var
from textual.widgets import DirectoryTree, Footer, Header, TextArea


class TextEditor(App):
    """Textual code editor app."""

    CSS = """
    #tree-view {
        display: none;
        scrollbar-gutter: stable;
        overflow: auto;
        width: auto;
        height: 100%;
        dock: left;
    }

    TextEditor.-show-tree #tree-view {
        display: block;
        max-width: 50%;
    }

    #code {
        overflow: auto scroll;
        max-width: 100%;
    }
    """
    
    BINDINGS = [
        ("f", "toggle_files", "Toggle Files"),
        ("q", "quit", "Quit"),
        ("s", "save", "Save File"),
        ("n", "new", "New File")
    ]

    show_tree = var(True)
    file_path = var('./' if len(sys.argv) < 2 else sys.argv[1])

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Compose our UI."""
        path = "./" if len(sys.argv) < 2 else sys.argv[1]
        yield Header(show_clock=True)
        with Container():
            yield DirectoryTree(self.file_path, id="tree-view")
            yield TextArea(id="code")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        code_view = self.query_one("#code", TextArea)
        sub_title = self.query_one(Header).screen_sub_title
        try:
            code_view.clear()
            file = open(event.path, 'r')
            code_view.load_text(file.read())
            sub_title = self.file_path = event.path
        except Exception:
            sub_title = "ERROR FILE OPENING"
        finally:
            file.close()

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

    def action_save(self) -> None:
        """Called in response to key binding."""
        sub_title = self.query_one(Header).screen_sub_title
        text = self.query_one('#code', TextArea).text
        if sub_title != "":
            try:
                file = open(self.file_path, 'w')
                file.write(text)
            except:
                sub_title = "ERROR SAVING FILE"
            finally:
                file.close()
        else:
            self.action_new()

    def action_new(self) -> None:
        """Called in respone to key binding."""
        sub_title = self.query_one(Header).screen_sub_title
        text = self.query_one('#code', TextArea).text
        try:
            file = open("./newfile", 'w')
            file.write(text)
        except:
            sub_title = "ERROR SAVING NEW FILE"
        finally:
            file.close()


if __name__ == "__main__":
    TextEditor().run()
