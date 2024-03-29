from textual.widgets.text_area import Selection
from textual.containers import Container
from textual.widgets import ListView
from textual.messages import Message

from pathlib import Path
import configparser
import git # poetry add gitpython
import os


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


# check files that have changes
# main_app is Main class from main.py
def check_git_diff(main_app: "Main") -> None:
    store = read_ini_file("stores.ini", "WorkingDirectory")
    git_dir = os.path.join(store["project_root"], ".git")
    
    if os.path.exists(git_dir) is False:
        return None

    repo = git.Repo(store["project_root"])
    changed_files = [f"{store['project_root']}/{item.a_path}" for item in repo.index.diff(None)]

    for content in main_app.query("DirectoryContentText"):
        if content.content_path in changed_files:
            content.set_to_git_changes_detected()
        else:
            content.styles.color = "white"


class SidebarUtils:
    def __init__(self, sidebar: "Sidebar") -> None:
        self.sidebar = sidebar

    # used to represent each file and directory in sidebar for dir_tree
    # before changed to DirectoryContentText widget for dir_tree_listview
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

    # re_mount the listview in sidebar
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
