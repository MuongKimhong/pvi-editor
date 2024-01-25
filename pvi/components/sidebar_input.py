###########################################################
#                                                         #
# An input inside sidebar used to create/append new files #
# or directories                                          #
#                                                         #
###########################################################

from textual.app import ComposeResult
from textual.widgets import Input
from textual import events

from utils import read_ini_file

from pathlib import Path
import os


class SidebarInput(Input):
    def __init__(self, highlighted_content: "DirectoryContentText") -> None:
        self.highlighted_content = highlighted_content
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        super().__init__()

    def set_style(self) -> None:
        self.styles.border = ("solid", "white")
        self.styles.background = "#131212"

    # highlighted_content in sidebar when create_new_file is called
    def create_new_file_or_dir(self) -> None:
        type_to_create = "file" if "." in self.value else "dir"
        sidebar = self.app.query_one("Sidebar")
        in_project_root = False        

        # check path to create
        if self.highlighted_content.content_type == "file":
            parent_path = os.path.dirname(self.highlighted_content.content_path)

            if parent_path == self.store["project_root"]:
                in_project_root = True

            # path for file or directory that is about to create
            new_data_path = parent_path + "/" + self.value
        else:
            new_data_path = self.highlighted_content.content_path + "/" + self.value

        # create file or directory
        if type_to_create == "file":
            new_file = open(new_data_path, "w")
            new_file.close()
        else:
            os.makedirs(new_data_path, exist_ok=True)

        from textual import log 
        log(f"check all files and all dirs")
        log(sidebar.all_files)
        log(sidebar.all_directories)

        if in_project_root:
            if type_to_create == "file":
                content_as_dict = sidebar.utils.content_as_dict(
                    "file", self.value, 0, new_data_path
                )
                sidebar.dir_tree = sidebar.dir_tree[:-len(sidebar.all_files)]
                sidebar.all_files.append(content_as_dict)
                sidebar.all_files = sorted(sidebar.all_files, key=lambda x: x["content"])
                sidebar.dir_tree = [*sidebar.dir_tree, *sidebar.all_files]
            else:
                content_as_dict = sidebar.utils.content_as_dict(
                    "dir", self.value + "/", 0, new_data_path
                )
                sidebar.dir_tree.insert(0, content_as_dict)

            sidebar.utils.handle_re_mount_listview()
        else:
            for content in sidebar.query("DirectoryContentText"):
                if content.content_path == str(Path(self.highlighted_content.content_path).parent):
                    sidebar.close_directory(content)
                    sidebar.open_directory(content)
                    break

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
