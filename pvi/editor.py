from textual.widgets import Static, ListView, ListItem, TextArea
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from utils import read_store_ini_file, update_store_ini_file, read_setting_ini_file
from components.main_editor import MainEditor
from components.sidebar import Sidebar

import time
import os


class Editor(Screen):
    CSS_PATH = "styles/style.tcss"

    def __init__(self):
        self.sidebar_style = read_setting_ini_file(section_name="Sidebar")
        self.store = read_store_ini_file(section_name="WorkingDirectory")
        self.focused_main_editor = True
        super().__init__()

    def compose(self) -> ComposeResult:
        yield MainEditor()

    def toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        width = sidebar.styles.width.value

        if int(width) == int(self.sidebar_style["max_width"]): sidebar.hide_sidebar()
        else: sidebar.show_sidebar()

    def mount_sidebar_to_screen(self) -> None:
        sidebar = Sidebar(dir_tree=os.listdir(self.store["editing_path"]))
        self.mount(sidebar)
        sidebar.scroll_visible()

    def sidebar_exists(self) -> bool:
        try:
            sidebar = self.query_one(Sidebar)
            return True
        except NoMatches:
            return False

    # Handle switch focus between Sidebar and Main Editor
    def handle_switching_focus(self) -> None:
        if self.sidebar_exists():
            if self.focused_main_editor:
                self.query_one(Sidebar).focus()
                self.focused_main_editor = False
            else:
                self.query_one(MainEditor).focus()
                self.focused_main_editor = True

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+b": # toggle sidebar
            if self.store["editing_type"] == "dir":
                if not self.sidebar_exists(): self.mount_sidebar_to_screen()

                self.toggle_sidebar()    

        elif event.key == "ctrl+q":
            if self.query_one(MainEditor).editing_mode == "normal":
                self.handle_switching_focus()

        elif event.key == "j":
            if self.focused_main_editor: # key binding move down in Main editor
                pass
            else:
                self.query_one(Sidebar).move_down()

        elif event.key == "k":
            if self.focused_main_editor:
                pass
            else:
                self.query_one(Sidebar).move_up()

        elif event.key == "enter":
            if self.focused_main_editor:
                pass
            else:
                selected_content_index = self.query_one(Sidebar).viewing["id"] - 1
                selected_content = self.query("DirectoryContentText")[selected_content_index]

                if selected_content.content_type == "file":
                    with open(f"{self.store['editing_path']}/{selected_content.content_name}", "r") as file:
                        self.handle_switching_focus()
                        self.query_one(MainEditor).handle_load_content_to_textarea(file_content=file.read())
                        
    def on_mount(self, event: events.Mount) -> None:
        pass

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        pass

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        pass
