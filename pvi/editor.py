from textual.widgets import Static, ListView, ListItem
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from utils import read_store_ini_file, update_store_ini_file
from utils import read_setting_ini_file
from components.sidebar import Sidebar
from components.main_editor import MainEditor
from components.welcome_text import WelcomeText

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
        
    def hide_sidebar(self) -> None:
        self.query_one(Sidebar).styles.width = 0
        self.query_one(Sidebar).styles.border = ("hidden", "grey")
    
    def show_sidebar(self) -> None:
        self.query_one(Sidebar).set_style()

    def toggle_sidebar(self) -> None:
        width = self.query_one(Sidebar).styles.width.value

        if int(width) == int(self.sidebar_style["max_width"]): self.hide_sidebar()
        else: self.show_sidebar()

    def mount_sidebar_to_screen(self) -> None:
        sidebar = Sidebar(dir_tree=os.listdir(self.store["editing_path"]))
        self.mount(sidebar)
        sidebar.scroll_visible()

    def sidebar_exists(self) -> bool:
        try:
            sidebar = self.query_one(Sidebar)
        except NoMatches:
            return False
        return True

    def mount_welcome_text(self) -> None:
        # Mount welcome text to Main Editor
        welcome_text = WelcomeText()
        self.query_one(MainEditor).mount(welcome_text)
        welcome_text.scroll_visible()

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
            self.handle_switching_focus()

        elif event.key == "j":
            if self.focused_main_editor: # key binding move down in Main editor
                pass
            else: # key binding move down in Sidebar
                pass

    def on_mount(self, event: events.Mount) -> None:
        if self.store["editing_type"] == "dir":
            self.mount_welcome_text()

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        pass

    def on_screen_suspend(self, event: events.ScreenSuspend) -> None:
        pass
