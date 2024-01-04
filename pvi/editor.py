from textual.widgets import Static, ListView, ListItem, TextArea, Input
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from components.main_editor import MainEditor
from components.sidebar import Sidebar
from utils import read_ini_file

import time
import os


class Editor(Screen):
    CSS_PATH = "styles/style.tcss"

    def __init__(self):
        self.sidebar_style = read_ini_file(file_name="settings.ini", section_name="Sidebar")
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        self.focused_main_editor = True
        self.typed_key = ""
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
                sidebar = self.query_one(Sidebar)
                sidebar_listview = sidebar.query_one("#sidebar-container").query_one("#listview")

                sidebar.move_down(editor=self)
                sidebar_listview.scroll_down()

        elif event.key == "k":
            if self.focused_main_editor:
                pass
            else:
                sidebar = self.query_one(Sidebar)
                sidebar_listview = sidebar.query_one("#sidebar-container").query_one("#listview")

                sidebar.move_up(editor=self)
                sidebar_listview.scroll_up()
 
        elif event.key == "a" and self.typed_key == "": 
            self.typed_key = self.typed_key + event.key
 
        #keybinding <af> append new file in highlighted directory,
        #or append in project root if no directory is highlighted 
        elif self.typed_key == "a" and event.key == "f": 
            if self.focused_main_editor is False:
                self.typed_key = ""
                self.query_one(Sidebar).mount_input(create_type="file")
                self.query_one(Sidebar).query_one("SidebarInput").focus()

        elif event.key == "enter":
            if self.focused_main_editor:
                pass
            else:
                selected_content_index = self.query_one(Sidebar).viewing_id - 1
                selected_content = self.query("DirectoryContentText")[selected_content_index]

                # enter on files
                if selected_content.content_type == "file":
                    self.query_one(Sidebar).select_file(selected_content=selected_content)
                    self.handle_switching_focus()
                
                # enter on directories
                else:
                    self.query_one(Sidebar).select_directory(selected_dir=selected_content)
                    self.query_one(Sidebar).focus()
                    self.focused_main_editor = False
                        
    def on_mount(self, event: events.Mount) -> None:
        pass

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        pass

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        pass
