###########################################################
#                                                         #
# An input inside sidebar used to create/append new files #
# or directories                                          #
#                                                         #
###########################################################

from textual.app import ComposeResult
from textual.widgets import Input
from textual import events, log

from utils import read_ini_file

import os


class SidebarInput(Input):
    def __init__(self, highlighted_content) -> None:
        self.highlighted_content = highlighted_content
        super().__init__()

    def set_style(self) -> None:
        self.styles.border = ("solid", "white")

    # highlighted_content in sidebar when create_new_file is called
    def create_new_file(self) -> None:
        data_to_create: str = self.value
        type_to_create = "file" if "." in data_to_create else "dir"
        sidebar = self.app.query_one("Sidebar")

        if self.highlighted_content.content_type == "file":
            new_data_path = os.path.dirname(self.highlighted_content.content_path) + "/" + data_to_create
        else:
            new_data_path = self.highlighted_content.content_path + "/" + data_to_create

        if type_to_create == "file":
            new_file = open(new_data_path, "w")
            new_file.close()
        else:
            os.makedirs(new_data_path, exist_ok=True)

        sidebar.highlighted_content = None
        sidebar.focus()
        self.remove()

    def on_mount(self, event: events.Mount) -> None:
        self.set_style()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape": # cancel the action
            self.app.query_one("Sidebar").focus()
            self.remove()

        elif event.key == "enter":
            self.create_new_file() 

    def on_focus(self, event: events.Focus) -> None:
        log("sidebar input is focus")
