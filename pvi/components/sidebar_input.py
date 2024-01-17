###########################################################
#                                                         #
# An input inside sidebar used to create/append new files #
# or directories                                          #
#                                                         #
###########################################################

from textual.app import ComposeResult
from textual.widgets import Input
from textual import events, log

from components.directory_content_text import DirectoryContentText
from utils import read_ini_file

from pathlib import Path
import time
import os


class SidebarInput(Input):
    def __init__(self, highlighted_content: DirectoryContentText) -> None:
        self.highlighted_content = highlighted_content
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        super().__init__()

    def set_style(self) -> None:
        self.styles.border = ("solid", "white")

    # highlighted_content in sidebar when create_new_file is called
    def create_new_file_or_dir(self) -> None:
        data_to_create: str = self.value
        type_to_create = "file" if "." in data_to_create else "dir"
        sidebar = self.app.query_one("Sidebar")
        in_project_root = False

        # check path to create
        if self.highlighted_content.content_type == "file":
            parent_path = os.path.dirname(self.highlighted_content.content_path)
            new_data_path = parent_path + "/" + data_to_create

            if parent_path == self.store["project_root"]:
                in_project_root = True
        else:
            new_data_path = self.highlighted_content.content_path + "/" + data_to_create

        # create file or directory
        if type_to_create == "file":
            new_file = open(new_data_path, "w")
            new_file.close()
        else:
            os.makedirs(new_data_path, exist_ok=True)

        if in_project_root:
            if type_to_create == "file":
                content_as_dict = sidebar.utils.content_as_dict(
                    "file", data_to_create, 0, new_data_path
                )
                sidebar.all_files.append(content_as_dict)
                sidebar.all_files = sorted(sidebar.all_files, key=lambda x: x["content"])
            else:
                content_as_dict = sidebar.utils.content_as_dict(
                    "dir", data_to_create + "/", 0, new_data_path
                )
                sidebar.all_directories.append(content_as_dict)
                sidebar.all_directories = sorted(sidebar.all_directories, key=lambda x: x["content"]) 
            
            sidebar.dir_tree = [*sidebar.all_directories, *sidebar.all_files]
            sidebar.utils.handle_re_mount_listview()
        else:
            sidebar.close_directory(selected_dir=self.highlighted_content)
            sidebar.open_directory(selected_dir=self.highlighted_content)

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
            self.create_new_file_or_dir() 
