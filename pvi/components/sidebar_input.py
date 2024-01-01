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
    def __init__(self, create_type, selected_directory=None) -> None:
        self.create_type = create_type # "file" or "dir"
        self.selected_directory = selected_directory
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        super().__init__()

    def set_style(self) -> None:
        self.styles.border = ("solid", "white")

    def create_new_file(self) -> None:
        file_name = self.value  

        if self.selected_directory is None:
            new_file = open(f"{self.store['editing_path']}/{file_name}", "w")
        else:
            new_file = open(f"{self.store['editing_path']}/{self.selected_directory}/{file_name}", "w")

        new_file.close()
        self.app.query_one("Sidebar").focus
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
