from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from utils import read_ini_file, update_ini_file
from components.sidebar import Sidebar

import os


class Editor(Screen):
    CSS_PATH = "styles/style.tcss"
    dir_tree_listview = ListView(*[], id="dir_tree_listview")

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Two", id="editor")
        
    def hide_sidebar(self) -> None:
        self.query_one(Sidebar).styles.width = 0
        self.query_one(Sidebar).styles.border = ("hidden", "grey")
    
    def show_sidebar(self) -> None:
        self.query_one(Sidebar).styles.width = 30
        self.query_one(Sidebar).styles.border = ("round", "#242424")
        self.query_one(Sidebar).styles.border_right = ("round", "grey")
        self.query_one(Sidebar).styles.border_top = ("round", "grey")

    def toggle_sidebar(self) -> None:
        width = self.query_one(Sidebar).styles.width.value

        if width == 30: self.hide_sidebar()
        else: self.show_sidebar()

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+b":
            self.toggle_sidebar()    

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        store = read_ini_file(section_name="WorkingDirectory")
        
        if store["editing_type"] == "file": self.hide_sidebar()
        else: self.show_sidebar()

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        pass
