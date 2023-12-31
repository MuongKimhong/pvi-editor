from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.app import ComposeResult
from textual.widget import Widget
from textual import log, events

from utils import read_store_ini_file, update_store_ini_file, read_setting_ini_file
from components.sidebar_input import SidebarInput

import time
import os


class DirectoryContentText(Container):
    def __init__(self, content_name: str, content_type: str, content_id: int, layer_level: int) -> None:
        self.content_name: str = content_name
        self.content_type: str = content_type
        self.content_id: int = content_id
        self.layer_level: int = layer_level + 1 if layer_level > 0 else 0
        self.state = "close"
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
        self.query_one(Static).styles.padding = (0, 0, 0, self.layer_level)
            

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
        super().__init__()

    def set_style(self) -> None:
        style = read_setting_ini_file(section_name="Sidebar")
        self.styles.border = (style["border_style"], f"#{style['border_color']}")
        self.styles.border_top = (style["border_top_style"], f"#{style['border_top_color']}")
        self.styles.border_right = (style["border_right_style"], f"#{style['border_right_color']}")
        self.styles.width = int(style["max_width"])

    def init_dir_tree(self) -> None:
        for content in self.dir_tree:
            if os.path.isfile(f"{self.store['editing_path']}/{content}"):
                self.all_files.append({"type": "file", "content": content, "layer_level": 0})
            elif os.path.isdir(f"{self.store['editing_path']}/{content}") and content != ".git":
                self.all_directories.append({"type": "dir", "content": f"{content}/", "layer_level": 0})

        self.all_files = sorted(self.all_files, key=lambda x: x["content"])
        self.all_directories = sorted(self.all_directories, key=lambda x: x["content"])
        self.dir_tree = self.all_directories + self.all_files 

    def init_dir_tree_listview(self) -> ListView:
        dir_tree_listview = ListView(*[], id="listview")

        for (index, content) in enumerate(self.dir_tree):
            content["id"] = index + 1

            if content["type"] == "dir":
                dir_tree_listview.append(
                    ListItem(
                        DirectoryContentText(
                            content_name=content["content"], 
                            content_type="dir", 
                            content_id=index+1, 
                            layer_level=content["layer_level"]
                        ),
                        classes="dirlistitem"
                    )
                ) 
            else:
                dir_tree_listview.append(
                    ListItem(
                        DirectoryContentText(
                            content_name=content["content"], 
                            content_type="file", 
                            content_id=index+1,
                            layer_level=content["layer_level"]
                        ),
                        classes="filelistitem"
                    )
                )
        return dir_tree_listview

    def compose(self) -> ComposeResult:
        self.init_dir_tree()
        yield Container(self.init_dir_tree_listview(), id="sidebar-container") 

    # get selected directory from store.ini
    # as it's already updated via update_store_ini_file function
    def select_directory(self, selected_dir: DirectoryContentText) -> None:
        log(f"State {selected_dir.state}")
        contents_above_selected_dir = []
        contents_below_selected_dir = []

        def handle_re_mount_listview(self):
            dir_tree_listview = self.init_dir_tree_listview() 
            self.query_one(ListView).remove()
            self.query_one(Container).mount(dir_tree_listview)
            dir_tree_listview.scroll_visible()

        if selected_dir.state == "close":
            selected_dir.state = "open"

            #remove / from content_name
            content_name = selected_dir.content_name[:len(selected_dir.content_name) - 1]

            self.store["editing_path"] = f"{self.store['editing_path']}/{content_name}"
            log(self.store)
            log(self.store["editing_path"])
            update_store_ini_file(section_name="WorkingDirectory", section_data=self.store)

            for (index, content) in enumerate(self.dir_tree):
                if content["id"] == selected_dir.content_id:
                    contents_above_selected_dir = self.dir_tree[:index + 1]
                    contents_below_selected_dir = self.dir_tree[index + 1:]

            selected_dir_contents = os.listdir(self.store["editing_path"])
            files_in_selected_dir_contents = []
            directories_in_selected_dir_contents = []

            for content in selected_dir_contents:
                if os.path.isfile(f"{self.store['editing_path']}/{content}"):
                    files_in_selected_dir_contents.append(
                        {"type": "file", "content": content, "layer_level": selected_dir.layer_level + 1}
                    )
                elif os.path.isdir(f"{self.store['editing_path']}/{content}") and content != ".git":
                    directories_in_selected_dir_contents.append(
                        {"type": "dir", "content": f"{content}/", "layer_level": selected_dir.layer_level + 1}
                    )

            sorted_files = sorted(files_in_selected_dir_contents, key=lambda x: x["content"])
            sorted_dirs = sorted(directories_in_selected_dir_contents, key=lambda x: x["content"])
            selected_dir_contents = sorted_files + sorted_dirs

            self.dir_tree = contents_above_selected_dir + selected_dir_contents + contents_below_selected_dir
            handle_re_mount_listview(self)

        elif selected_dir.state == "open":
            selected_dir.state = "close"
            selected_dir_contents = os.listdir(self.store["editing_path"])

            # update editing_path by removing the last directory
            splited = self.store["editing_path"].split("/")
            self.store["editing_path"] = "/".join(splited[:-1])
            update_store_ini_file(section_name="WorkingDirectory", section_data=self.store)
            
            for (index, content) in enumerate(self.dir_tree):
                if content["id"] == selected_dir.content_id:
                    contents_above_selected_dir = self.dir_tree[:index + 1]
                    contents_below_selected_dir = self.dir_tree[index + 1 + len(selected_dir_contents):]

            self.dir_tree = contents_above_selected_dir + contents_below_selected_dir
            handle_re_mount_listview(self)

        for content in self.query("DirectoryContentText"):
            if content.content_id == self.viewing_id:
                content.set_to_highlighted()
            else:
                content.set_to_normal()

    def select_file(self, selected_content: DirectoryContentText) -> None:
        with open(f"{self.store['editing_path']}/{selected_content.content_name}", "r") as file:
            self.app.query_one("MainEditor").handle_load_content_to_textarea(file_content=file.read())

    def hide_sidebar(self) -> None:
        self.styles.width = 0
        self.styles.border = ("hidden", "grey")

    def show_sidebar(self) -> None:
        self.set_style()

    def handle_set_to_highlighted_or_normal(self, move_direction: str, editor) -> None:
        self.viewing_id = self.viewing_id - 1 if move_direction == "up" else self.viewing_id + 1

        for content in self.query("DirectoryContentText"):
            if content.content_id == self.viewing_id:
                content.set_to_highlighted()
            else:
                content.set_to_normal()

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
        self.set_style() 

    def on_focus(self, event: events.Focus) -> None:
        for content in self.query("DirectoryContentText"):
            if content.content_id == self.viewing_id:
                content.set_to_highlighted()
            else:
                content.set_to_normal()
        
    def on_blur(self, event: events.Blur) -> None:
        for content in self.query("DirectoryContentText"):
            content.set_to_normal() 