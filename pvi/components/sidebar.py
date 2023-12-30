from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.widget import Widget
from textual import log, events

from utils import read_store_ini_file, update_store_ini_file, read_setting_ini_file
from components.sidebar_input import SidebarInput

import os


class DirectoryContentText(Container):
    def __init__(self, content_name: str, content_type: str, content_id: int) -> None:
        self.content_name: str = content_name
        self.content_type: str = content_type
        self.content_id: int = content_id
        super().__init__()

    def compose(self) -> None:
        yield Static(self.content_name)

    def set_to_highlighted(self) -> None:
        self.styles.background = "grey"
        self.styles.text_style = "bold"
        self.styles.color = "cyan" if self.content_type == "dir" else "white"

    def set_to_normal(self) -> None:
        self.styles.background = "#242424"
        if self.content_type == "dir":
            self.styles.color = "cyan"
            self.styles.text_style = "bold"
        else:
            self.styles.color = "white"

    def on_mount(self, event: events.Mount) -> None:
        self.set_to_normal()
            

class Sidebar(Container, can_focus=True):
    DEFAULT_CSS = """
    Sidebar #listview {
        background: #242424;
    }
    """
    def __init__(self, dir_tree: list):
        self.dir_tree = dir_tree
        self.dir_tree_listview = ListView(*[], id="listview")

        # represent viewing directory, file and indexing in directory tree
        self.viewing = {
            "directory_name": "", 
            "file_name": "",
            "id": 1, # viewing index inside directory tree
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
                # files.append(content)
                files.append({"type": "file", "content": content, "nested": []})
            elif os.path.isdir(f"{directory_path}/{content}") and content != ".git":
                # directories.append(content)
                directories.append({"type": "dir", "content": f"{content}/", "nested": []})

        sorted_files = sorted(files, key=lambda x: x["content"])
        sorted_directories = sorted(directories, key=lambda x: x["content"])

        self.dir_tree = sorted_directories + sorted_files

        for (index, content) in enumerate(self.dir_tree):
            content["id"] = index + 1

            if content["type"] == "dir":
                self.dir_tree_listview.append(
                    ListItem(
                        DirectoryContentText(content_name=content["content"], content_type="dir", content_id=index+1),
                        classes="dirlistitem", id=f"dir-item-{index+1}"
                    )
                ) 
            else:
                self.dir_tree_listview.append(
                    ListItem(
                        DirectoryContentText(content_name=content["content"], content_type="file", content_id=index+1),
                        classes="filelistitem", id=f"file-item-{index+1}"
                    )
                )

        yield Container(self.dir_tree_listview, id="sidebar-container") 

    def hide_sidebar(self) -> None:
        self.styles.width = 0
        self.styles.border = ("hidden", "grey")

    def show_sidebar(self) -> None:
        self.set_style()

    def handle_set_to_highlighted_or_normal(self, move_direction: str, editor) -> None:
        self.viewing["id"] = self.viewing.get("id") - 1 if move_direction == "up" else self.viewing.get("id") + 1

        for content in self.query("DirectoryContentText"):
            if content.content_id == self.viewing.get("id"):
                content.set_to_highlighted()
                editor.sidebar_highlighting_type = content.content_type
            else:
                content.set_to_normal()

    def move_down(self, editor) -> None:
        if self.viewing.get("id") < len(self.query("DirectoryContentText")):
            self.handle_set_to_highlighted_or_normal(move_direction="down", editor=editor)

    def move_up(self, editor) -> None:
        if self.viewing.get("id") > 1:
            self.handle_set_to_highlighted_or_normal(move_direction="up", editor=editor)

    def mount_input(self, create_type: str) -> None:
        sidebar_input = SidebarInput(create_type=create_type)
        self.mount(sidebar_input)
        sidebar_input.scroll_visible()

    def on_focus(self, event: events.Focus) -> None:
        for content in self.query("DirectoryContentText"):
            if content.content_id == self.viewing["id"]:
                content.set_to_highlighted()
            else:
                content.set_to_normal()
        
    def on_blur(self, event: events.Blur) -> None:
        for content in self.query("DirectoryContentText"):
            content.set_to_normal() 