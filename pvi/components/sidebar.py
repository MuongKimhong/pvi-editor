from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual import log

from utils import read_store_ini_file, update_store_ini_file

import os


class Sidebar(Static):
    def __init__(self, dir_tree: list):
        self.dir_tree = dir_tree
        self.dir_tree_listview = ListView(*[], id="listview")
        super().__init__()

    def compose(self) -> ComposeResult:
        directory_path = read_store_ini_file("WorkingDirectory")["directory_path"]

        for content in self.dir_tree:
            if os.path.isfile(f"{directory_path}/{content}"):
                self.dir_tree_listview.append(ListItem(Static(content), classes="filelistitem"))
            elif os.path.isdir(f"{directory_path}/{content}"):
                self.dir_tree_listview.append(ListItem(Static(f"{content}/"), classes="dirlistitem"))

        yield Container(self.dir_tree_listview, id="sidebar-container")
        yield Static("", id="sidebar")

     