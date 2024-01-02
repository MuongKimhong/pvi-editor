from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.widget import Widget
from textual import log, events

from utils import read_ini_file, update_ini_file
from utils import SidebarUtils

from components.directory_content_text import DirectoryContentText
from components.sidebar_input import SidebarInput

import time
import os
            

class Sidebar(Container, can_focus=True):
    DEFAULT_CSS = """
    Sidebar #listview {
        background: #181717;
    }
    """
    def __init__(self, dir_tree: list):
        self.all_files = []
        self.all_directories = []

        self.dir_tree = dir_tree
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        self.viewing_id = 1 # viewing index inside directory tree (sidebar)

        self.content_states = {}
        self.utils = SidebarUtils(self)
        super().__init__()

    def list_item(self, content, c_id, c_type) -> ListItem:
        class_name = "filelistitem" if c_type == "file" else "dirlistitem"
        dc = DirectoryContentText(content["content"], c_type, c_id, content["layer_level"])
        return ListItem(dc, classes=class_name, id=f"listitem-{c_id}")

    def init_dir_tree(self) -> None:
        for content in self.dir_tree:
            if os.path.isfile(f"{self.store['editing_path']}/{content}"):
                self.all_files.append(
                    self.utils.content_as_dict("file", content, 0)
                )
            elif os.path.isdir(f"{self.store['editing_path']}/{content}") and content != ".git":
                self.all_directories.append(
                    self.utils.content_as_dict("dir", f"{content}/", 0)
                )

        self.all_files = sorted(self.all_files, key=lambda x: x["content"])
        self.all_directories = sorted(self.all_directories, key=lambda x: x["content"])
        self.dir_tree = self.all_directories + self.all_files 

    def init_dir_tree_listview(self) -> ListView:
        dir_tree_listview = ListView(*[], id="listview")

        for (index, content) in enumerate(self.dir_tree):
            content["id"] = _id = index + 1
            self.content_states[f"content_{_id}"] = "close"

            if self.content_states.get(f"content_{_id}") is None:
                self.content_states[f"content_{_id}"] = "close"

            if content["type"] == "dir":
                dir_tree_listview.append(self.list_item(content, _id, "dir")) 
            else:
                dir_tree_listview.append(self.list_item(content, _id, "file"))
        return dir_tree_listview

    def compose(self) -> ComposeResult:
        self.init_dir_tree()
        yield Container(self.init_dir_tree_listview(), id="sidebar-container") 

    def open_directory(self, selected_dir: DirectoryContentText) -> None:
        # remove / from content_name
        content_name = selected_dir.content_name[:len(selected_dir.content_name) - 1]
        self.store["editing_path"] = f"{self.store['editing_path']}/{content_name}"
        update_ini_file(file_name="stores.ini", section_name="WorkingDirectory", section_data=self.store)

        for (index, content) in enumerate(self.dir_tree):
            if content["id"] == selected_dir.content_id:
                contents_above_selected_dir = self.dir_tree[:index + 1]
                contents_below_selected_dir = self.dir_tree[index + 1:]

        selected_dir_contents = os.listdir(self.store["editing_path"])
        files_in_selected_dir_contents = []
        directories_in_selected_dir_contents = []

        for content in selected_dir_contents:
            layer = selected_dir.layer_level + 1

            if os.path.isfile(f"{self.store['editing_path']}/{content}"):
                files_in_selected_dir_contents.append(
                    self.utils.content_as_dict("file", content, layer)
                )
            elif os.path.isdir(f"{self.store['editing_path']}/{content}") and content != ".git":
                directories_in_selected_dir_contents.append(
                    self.utils.content_as_dict("dir", f"{content}/", layer)
                )

        selected_dir_contents = [
            *sorted(files_in_selected_dir_contents, key=lambda x: x["content"]),
            *sorted(directories_in_selected_dir_contents, key=lambda x: x["content"])
        ]
        self.dir_tree = [
            *contents_above_selected_dir, 
            *selected_dir_contents, 
            *contents_below_selected_dir
        ]
        self.utils.handle_re_mount_listview()
        self.content_states[f"content_{selected_dir.content_id}"] = "open"

    def close_directory(self, selected_dir: DirectoryContentText) -> None:
        selected_dir_contents = os.listdir(self.store["editing_path"])

        # update editing_path by removing the last directory
        splited = self.store["editing_path"].split("/")
        self.store["editing_path"] = "/".join(splited[:-1])
        update_ini_file(file_name="stores.ini", section_name="WorkingDirectory", section_data=self.store)
        
        for (index, content) in enumerate(self.dir_tree):
            if content["id"] == selected_dir.content_id:
                contents_above_selected_dir = self.dir_tree[:index + 1]
                contents_below_selected_dir = self.dir_tree[index + 1 + len(selected_dir_contents):]

        self.dir_tree = [*contents_above_selected_dir, *contents_below_selected_dir]
        self.utils.handle_re_mount_listview()
        self.content_states[f"content_{selected_dir.content_id}"] = "close"

    # get selected directory from store.ini
    # as it's already updated via update_store_ini_file function
    def select_directory(self, selected_dir: DirectoryContentText) -> None:
        if self.content_states[f"content_{selected_dir.content_id}"] == "close":
            self.open_directory(selected_dir=selected_dir)

        elif self.content_states[f"content_{selected_dir.content_id}"] == "open":
            self.close_directory(selected_dir=selected_dir)

        self.utils.set_to_highlighted_or_normal()

    def select_file(self, selected_content: DirectoryContentText) -> None:
        for content in self.query("DirectoryContentText"):
            if content.content_id == selected_content.content_id:
                content.file_opened = True
                content.set_to_highlighted_after_selected_file()
            else:
                content_file_opened = False

        with open(f"{self.store['editing_path']}/{selected_content.content_name}", "r") as file:
            self.app.query_one("MainEditor").handle_load_content_to_textarea(
                file_content=file.read(),
                file_name=selected_content.content_name
            )

    def hide_sidebar(self) -> None:
        self.styles.width = 0
        self.styles.border = ("hidden", "grey")

    def show_sidebar(self) -> None:
        self.utils.set_sidebar_style()

    def handle_set_to_highlighted_or_normal(self, move_direction: str, editor) -> None:
        self.viewing_id = self.viewing_id - 1 if move_direction == "up" else self.viewing_id + 1
        self.utils.set_to_highlighted_or_normal()

    def move_down(self, editor) -> None:
        if self.viewing_id < len(self.query("DirectoryContentText")):
            self.handle_set_to_highlighted_or_normal(move_direction="down", editor=editor)

    def move_up(self, editor) -> None:
        if self.viewing_id > 1:
            self.handle_set_to_highlighted_or_normal(move_direction="up", editor=editor)

    def mount_input(self, create_type: str) -> None:
        sidebar_input = SidebarInput(create_type=create_type)
        self.mount(sidebar_input)
        sidebar_input.scroll_visible()

    def on_mount(self, event: events.Mount) -> None:
        self.utils.set_sidebar_style()

    def on_focus(self, event: events.Focus) -> None:
        self.utils.set_to_highlighted_or_normal()
        
    def on_blur(self, event: events.Blur) -> None:
        for content in self.query("DirectoryContentText"):
            if content.file_opened is False:
                content.set_to_normal()
