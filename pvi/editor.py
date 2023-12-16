from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from components.sidebar import Sidebar

import os


class Editor(Screen):
    CSS_PATH = "style.tcss"
    dir_tree_listview = ListView(*[], id="dir_tree_listview")

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Two", id="editor")

    def toggle_sidebar(self) -> None:
        width = self.query_one(Sidebar).styles.width.value

        self.query_one(Sidebar).styles.width = 0 if width == 30 else 30

        if width == 30:
            self.query_one(Sidebar).styles.border = ("hidden", "grey")
        else:
            self.query_one(Sidebar).styles.border = ("round", "#242424")
            self.query_one(Sidebar).styles.border_right = ("round", "grey")
            self.query_one(Sidebar).styles.border_top = ("round", "grey")

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+b":
            self.toggle_sidebar()    

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        pass

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        pass
