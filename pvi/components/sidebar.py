from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.widget import Widget
from textual import log, events

from utils import read_store_ini_file, update_store_ini_file
from utils import read_setting_ini_file

import os


class DirectoryContentText(Container):
    def __init__(self, content_name, content_type) -> None:
        self.content_name = content_name
        self.content_type = content_type
        super().__init__()

    def compose(self) -> None:
        yield Static(self.content_name)


class Sidebar(Container, can_focus=True):
    def __init__(self, dir_tree: list):
        self.dir_tree = dir_tree
        self.dir_tree_listview = ListView(*[], id="listview")

        # represent viewing directory, file and indexing in directory tree
        self.viewing = {
            "directory_name": "", 
            "file_name": "",
            "index": 0, # viewing index inside directory tree
            "next_index": None, 
            "previous_index": None,
        }
        super().__init__()

    def set_style(self) -> None:
        style = read_setting_ini_file(section_name="Sidebar")
        self.styles.border = (style["border_style"], f"#{style['border_color']}")
        self.styles.border_top = (style["border_top_style"], f"#{style['border_top_color']}")
        self.styles.border_right = (style["border_right_style"], f"#{style['border_right_color']}")
        self.styles.width = int(style["max_width"])

    def on_mount(self, event: events.Mount) -> None:
        self.set_style() 

    def compose(self) -> ComposeResult:
        directory_path = read_store_ini_file("WorkingDirectory")["editing_path"]
        directories = []
        files = []

        for content in self.dir_tree:
            if os.path.isfile(f"{directory_path}/{content}"):
                files.append(content)
            elif os.path.isdir(f"{directory_path}/{content}") and content != ".git":
                directories.append(content)

        files.sort()
        directories.sort()

        for directory in directories:
            self.dir_tree_listview.append(
                ListItem(
                    DirectoryContentText(content_name=f"{directory}/", content_type="dir"),
                    classes="dirlistitem"
                )
            )
        for file in files:
            self.dir_tree_listview.append(
                ListItem(
                    DirectoryContentText(content_name=file, content_type="file"),
                    classes="filelistitem"
                )
            )

        yield Container(self.dir_tree_listview, id="sidebar-container") 

    def on_focus(self, event: events.Focus) -> None:
        log("Sidebar is focused")