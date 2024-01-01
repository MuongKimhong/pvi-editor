from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.widget import Widget
from textual import log, events

from utils import read_store_ini_file, update_store_ini_file
from utils import set_sidebar_style, content_as_dict, set_to_highlighted_or_normal, handle_re_mount_listview

from components.directory_content_text import DirectoryContentText
from components.sidebar_input import SidebarInput

import time
import os
            

class Sidebar(Container, can_focus=True):
    DEFAULT_CSS = """
    Sidebar #listview {
        background: #242424;
    }
    """
    def __init__(self, dir_tree: list):
        self.all_files = []
        self.all_directories = []

        self.dir_tree = dir_tree
        self.store = read_store_ini_file(section_name="WorkingDirectory")
        self.viewing_id = 1 # viewing index inside directory tree (sidebar)

        self.content_states = {}
        super().__init__()

    def list_item(self, content, c_id, c_type) -> ListItem:
        class_name = "filelistitem" if c_type == "file" else "dirlistitem"
        dc = DirectoryContentText(content["content"], c_type, c_id, content["layer_level"])
        return ListItem(dc, classes=class_name, id=f"listitem-{c_id}")

    def init_dir_tree(self) -> None:
        for content in self.dir_tree:
            if os.path.isfile(f"{self.store['editing_path']}/{content}"):
                self.all_files.append(
                    content_as_dict("file", content, 0)
                )
            elif os.path.isdir(f"{self.store['editing_path']}/{content}") and content != ".git":
                self.all_directories.append(
                    content_as_dict("dir", f"{content}/", 0)
                )

        self.all_files = sorted(self.all_files, key=lambda x: x["content"])
        self.all_directories = sorted(self.all_directories, key=lambda x: x["content"])
        self.dir_tree = self.all_directories + self.all_files 

    def init_dir_tree_listview(self) -> ListView:
        dir_tree_listview = ListView(*[], id="listview")

        for (index, content) in enumerate(self.dir_tree):
            content["id"] = index + 1
            self.content_states[f"content_{index + 1}"] = "close"

            if content["type"] == "dir":
                dir_tree_listview.append(self.list_item(content, index+1, "dir")) 
            else:
                dir_tree_listview.append(self.list_item(content, index+1, "file"))
        return dir_tree_listview

    def compose(self) -> ComposeResult:
        self.init_dir_tree()
        yield Container(self.init_dir_tree_listview(), id="sidebar-container") 

    def open_directory(self, selected_dir: DirectoryContentText) -> None:
        # remove / from content_name
        content_name = selected_dir.content_name[:len(selected_dir.content_name) - 1]
        self.store["editing_path"] = f"{self.store['editing_path']}/{content_name}"
        update_store_ini_file(section_name="WorkingDirectory", section_data=self.store)

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
                    content_as_dict("file", content, layer)
                )
            elif os.path.isdir(f"{self.store['editing_path']}/{content}") and content != ".git":
                directories_in_selected_dir_contents.append(
                    content_as_dict("dir", f"{content}/", layer)
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
        handle_re_mount_listview(self)
        self.content_states[f"content_{selected_dir.content_id}"] = "open"

    def close_directory(self, selected_dir: DirectoryContentText) -> None:
        selected_dir_contents = os.listdir(self.store["editing_path"])

        # update editing_path by removing the last directory
        splited = self.store["editing_path"].split("/")
        self.store["editing_path"] = "/".join(splited[:-1])
        update_store_ini_file(section_name="WorkingDirectory", section_data=self.store)
        
        for (index, content) in enumerate(self.dir_tree):
            if content["id"] == selected_dir.content_id:
                contents_above_selected_dir = self.dir_tree[:index + 1]
                contents_below_selected_dir = self.dir_tree[index + 1 + len(selected_dir_contents):]

        self.dir_tree = [*contents_above_selected_dir, *contents_below_selected_dir]
        handle_re_mount_listview(self)
        self.content_states[f"content_{selected_dir.content_id}"] = "close"

    # get selected directory from store.ini
    # as it's already updated via update_store_ini_file function
    def select_directory(self, selected_dir: DirectoryContentText) -> None:
        if self.content_states[f"content_{selected_dir.content_id}"] == "close":
            self.open_directory(selected_dir=selected_dir)

        elif self.content_states[f"content_{selected_dir.content_id}"] == "open":
            self.close_directory(selected_dir=selected_dir)

        set_to_highlighted_or_normal(self)

    def select_file(self, selected_content: DirectoryContentText) -> None:
        with open(f"{self.store['editing_path']}/{selected_content.content_name}", "r") as file:
            self.app.query_one("MainEditor").handle_load_content_to_textarea(file_content=file.read())

    def hide_sidebar(self) -> None:
        self.styles.width = 0
        self.styles.border = ("hidden", "grey")

    def show_sidebar(self) -> None:
        set_sidebar_style(self)

    def handle_set_to_highlighted_or_normal(self, move_direction: str, editor) -> None:
        self.viewing_id = self.viewing_id - 1 if move_direction == "up" else self.viewing_id + 1
        set_to_highlighted_or_normal(self)

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
        set_sidebar_style(self)

    def on_focus(self, event: events.Focus) -> None:
        set_to_highlighted_or_normal(self)
        
    def on_blur(self, event: events.Blur) -> None:
        for content in self.query("DirectoryContentText"):
            if content.content_id == self.viewing_id:
                content.set_to_normal()
                break
