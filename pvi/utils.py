from textual.widgets.text_area import Selection
from textual.containers import Container
from textual.widgets import ListView
from textual.messages import Message
from textual import log

from pathlib import Path
import configparser


def get_pvi_root() -> Path:
    return Path(__file__).parent.parent


def read_ini_file(file_name: str, section_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read(f"{get_pvi_root()}/pvi/store/{file_name}")
    return config[section_name]


def update_ini_file(file_name: str, section_name: str, section_data: dict) -> None:
    config = configparser.ConfigParser()
    config.read(f"{get_pvi_root()}/pvi/store/{file_name}")
    config[section_name].update(section_data)

    with open(f"{get_pvi_root()}/pvi/store/{file_name}", "w") as configfile:
        config.write(configfile)


class SidebarUtils:
    def __init__(self, sidebar) -> None:
        self.sidebar = sidebar

    def set_sidebar_style(self) -> None:
        style = read_ini_file(file_name="settings.ini", section_name="Sidebar")
        self.sidebar.styles.border = (style["border_style"], f"#{style['border_color']}")
        self.sidebar.styles.border_top = (style["border_top_style"], f"#{style['border_top_color']}")
        self.sidebar.styles.border_right = (style["border_right_style"], f"#{style['border_right_color']}")
        self.sidebar.styles.width = int(style["max_width"])

    # used to represent each file and directory in sidebar
    # before changed to DirectoryContentText widget
    def content_as_dict(self, c_type: str, content: str, layer_level: int, c_path: str) -> dict:
        return {
            "type": c_type,
            "content": content,
            "layer_level": layer_level,
            "path": c_path
        }

    # set the DirectoryContentText to highligh or normal
    def set_to_highlighted_or_normal(self) -> None:
        for content in self.sidebar.query("DirectoryContentText"):
            if content.content_id == self.sidebar.viewing_id:
                content.set_to_highlighted()
            else:
                content.set_to_normal()

    # re_mount the listview in sidebar whenever user open a directory
    def handle_re_mount_listview(self):
        dir_tree_listview = self.sidebar.init_dir_tree_listview() 
        self.sidebar.query_one(ListView).remove()
        self.sidebar.query_one(Container).mount(dir_tree_listview)
        dir_tree_listview.scroll_visible()
        self.set_to_highlighted_or_normal()

    # get the instance of DirectoryContentText from provided content id from dir_tree
    def get_directory_content_text(self, content_id: int):
        for content in self.sidebar.query("DirectoryContentText"):
            if content.content_id == content_id:
                return content
