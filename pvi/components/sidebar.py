from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.widget import Widget
from textual import events

from utils import read_ini_file, update_ini_file
from utils import SidebarUtils

from components.directory_content_text import DirectoryContentText
from components.sidebar_input import SidebarInput
from textual.color import Color

import time
import os
            

class Sidebar(Container, can_focus=True):
    DEFAULT_CSS = """
    Sidebar #listview {
        background: #131212;
    }
    """

    def __init__(self, dir_tree: list, id=None, classes=None):
        self.all_files = []
        self.all_directories = []

        self.dir_tree = dir_tree
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        self.viewing_id = 1 # viewing index inside directory tree (sidebar)

        self.content_states = {}
        self.utils = SidebarUtils(self)

        # use this to make content stay highlighting when append new data 
        # with <aa> key binding
        self.highlighted_content: DirectoryContentText | None = None
        super().__init__(id=id, classes=classes)

    def list_item(self, content: dict, c_id: int) -> ListItem:
        class_name = "filelistitem" if content["type"] == "file" else "dirlistitem"

        dc = DirectoryContentText(
            content["content"], 
            content["type"], 
            c_id, 
            content["layer_level"], 
            content["path"]
        )
        return ListItem(dc, classes=class_name, id=f"listitem-{c_id}")

    def init_dir_tree(self) -> None:
        for index, content in enumerate(self.dir_tree):
            path = f"{self.store['editing_path']}/{content}"

            if os.path.isfile(path):
                self.all_files.append(
                    self.utils.content_as_dict("file", content, 0, path)
                )
            elif os.path.isdir(path) and content != ".git":
                self.all_directories.append(
                    self.utils.content_as_dict("dir", f"{content}/", 0, path)
                )
        self.all_files = sorted(self.all_files, key=lambda x: x["content"])
        self.all_directories = sorted(self.all_directories, key=lambda x: x["content"])
        self.dir_tree = [*self.all_directories, *self.all_files]

    def init_dir_tree_listview(self) -> ListView:
        dir_tree_listview = ListView(*[], id="listview")

        for (index, content) in enumerate(self.dir_tree):
            content["id"] = _id = index + 1

            if self.content_states.get(f"content_{_id}") is None:
                self.content_states[f"content_{_id}"] = "close"

            dir_tree_listview.append(self.list_item(content, _id))
        return dir_tree_listview

    def compose(self) -> ComposeResult:
        self.init_dir_tree()
        yield Container(self.init_dir_tree_listview(), id="sidebar-container") 

    def open_directory(self, selected_dir: DirectoryContentText, remount_listview=True) -> None:
        self.store["editing_path"] = selected_dir.content_path
        update_ini_file(
            file_name="stores.ini", 
            section_name="WorkingDirectory", 
            section_data=self.store
        )
        for (index, content) in enumerate(self.dir_tree):
            if content["id"] == selected_dir.content_id:
                contents_above_selected_dir = self.dir_tree[:index + 1]
                contents_below_selected_dir = self.dir_tree[index + 1:]

        selected_dir_contents = os.listdir(selected_dir.content_path)

        if len(selected_dir_contents) > 0:
            files_in_selected_dir_contents = []
            directories_in_selected_dir_contents = []

            layer = None

            for content in selected_dir_contents:
                layer = selected_dir.layer_level + 1
                path = f"{selected_dir.content_path}/{content}"

                if os.path.isfile(path):
                    files_in_selected_dir_contents.append(
                        self.utils.content_as_dict("file", content, layer, path)
                    )
                elif os.path.isdir(path) and content != ".git":
                    directories_in_selected_dir_contents.append(
                        self.utils.content_as_dict("dir", f"{content}/", layer, path)
                    )

            # increase sidebar width as number of layer increases
            if layer > 3:
                self.styles.width = self.styles.width.value + 1
            elif layer > 5:
                self.styles.width = self.styles.width.value + 2

            selected_dir_contents = [
                *sorted(directories_in_selected_dir_contents, key=lambda x: x["content"]),
                *sorted(files_in_selected_dir_contents, key=lambda x: x["content"])
            ]
            self.dir_tree = [
                *contents_above_selected_dir, 
                *selected_dir_contents, 
                *contents_below_selected_dir
            ]
            if remount_listview:
                self.utils.handle_re_mount_listview()

            self.content_states[f"content_{selected_dir.content_id}"] = "open"

    def close_directory(self, selected_dir: DirectoryContentText) -> None:
        content_to_remove = []

        for (index, content) in enumerate(self.dir_tree):
            dct = self.utils.get_directory_content_text(index + 1)

            if ((dct.layer_level > selected_dir.layer_level) and
                (selected_dir.content_path in content["path"])):
                content_to_remove.append(content)

        self.dir_tree = [content for content in self.dir_tree if content not in content_to_remove]
        self.utils.handle_re_mount_listview()
        self.content_states[f"content_{selected_dir.content_id}"] = "close"

    def select_directory(self, selected_dir: DirectoryContentText) -> None:
        state = self.content_states[f"content_{selected_dir.content_id}"]

        if state == "close":
            self.open_directory(selected_dir=selected_dir)
        else:
            self.close_directory(selected_dir=selected_dir)

    def select_file(self, selected_content: DirectoryContentText) -> None:
        not_spp_extension = [
            "png", "jpeg", "jpg", "JPEG", "JPG", "mp4", "mp3", "mov",
            "avi", "gif", "tiff", "bmp", "wmv", "flv", "mkv", "ogg",
            "wav", "wma", "flac", "aac", "docx", "doc", "xls", "xlsx",
            "pdf"
        ]
        if selected_content.content_name.split(".")[-1] not in not_spp_extension:
            for content in self.query("DirectoryContentText"):
                if content.content_id == selected_content.content_id:
                    content.file_opened = True
                    content.set_to_highlighted_after_selected_file()
                else:
                    content_file_opened = False

            with open(selected_content.content_path, "r") as file:
                self.app.query_one("MainEditor").handle_load_content_to_textarea(
                    file_content=file.read(),
                    file_name=selected_content.content_name
                )
                self.app.query_one("#header-text").update(selected_content.content_path)

                self.store["editing_path"] = selected_content.content_path
                update_ini_file(
                    file_name="stores.ini", 
                    section_name="WorkingDirectory", 
                    section_data=self.store
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

    def mount_input(self, highlighted_content: DirectoryContentText) -> None:
        self.highlighted_content = highlighted_content
        sidebar_input = SidebarInput(highlighted_content=highlighted_content)
        self.mount(sidebar_input)
        sidebar_input.focus()

    def on_mount(self, event: events.Mount) -> None:
        self.utils.set_sidebar_style()
        
        for content in self.query("DirectoryContentText"):
            content.set_to_normal()

    def on_focus(self, event: events.Focus) -> None:
        self.utils.set_to_highlighted_or_normal()
        
    def on_blur(self, event: events.Blur) -> None:
        for content in self.query("DirectoryContentText"):
            if content.file_opened is False:
                content.set_to_normal()
        
        if self.highlighted_content is not None: self.highlighted_content.set_to_highlighted()
