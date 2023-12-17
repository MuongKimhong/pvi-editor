from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from utils import read_store_ini_file, update_store_ini_file
from utils import read_setting_ini_file
from components.sidebar import Sidebar

import os


class Editor(Screen):
    CSS_PATH = "styles/style.tcss"

    def __init__(self):
        self.sidebar_style = read_setting_ini_file(section_name="Sidebar")
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Sidebar(dir_tree=os.listdir(read_store_ini_file("WorkingDirectory")["directory_path"]))
        yield Static("Two", id="editor")
        
    def hide_sidebar(self) -> None:
        self.query_one(Sidebar).styles.width = 0
        self.query_one(Sidebar).styles.border = ("hidden", "grey")
    
    def show_sidebar(self) -> None:
        self.query_one(Sidebar).set_style()

    def toggle_sidebar(self) -> None:
        width = self.query_one(Sidebar).styles.width.value

        if int(width) == int(self.sidebar_style["max_width"]): self.hide_sidebar()
        else: self.show_sidebar()

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+b":
            self.toggle_sidebar()    

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        store = read_store_ini_file(section_name="WorkingDirectory")
        
        if store["editing_type"] == "file": self.hide_sidebar()
        else: self.show_sidebar()

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        pass
