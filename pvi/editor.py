from textual.widgets import Static, ListView, ListItem, TextArea, Input
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.screen import Screen
from textual import events, log

from components.delete_dialog import DeleteDialog
from components.main_editor import MainEditor
from components.sidebar import Sidebar
from utils import read_ini_file

from pathlib import Path
import time
import os


class Editor(Screen):
    CSS_PATH = "styles/style.tcss"

    def __init__(self):
        self.sidebar_style = read_ini_file(file_name="settings.ini", section_name="Sidebar")
        self.store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")
        self.focused_main_editor = True

        self.typed_key = ""
        self.typed_key_timer: float | None = None
        self.selected_dir = None
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

    @property
    def sidebar_exists(self) -> bool:
        try:
            sidebar = self.query_one(Sidebar)
            return True
        except NoMatches:
            return False

    # Handle switch focus between Sidebar and Main Editor
    def handle_switching_focus(self) -> None:
        if self.sidebar_exists:
            if self.focused_main_editor:
                self.query_one(Sidebar).focus()
                self.focused_main_editor = False
            else:
                self.query_one(MainEditor).focus()
                self.focused_main_editor = True

    def reset_typed_key(self) -> None:
        self.typed_key = ""
        self.typed_key_timer = None

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+b" and self.store["argument_parser_type"] == "dir": # toggle sidebar
            if self.store["editing_type"] == "dir":
                if not self.sidebar_exists: 
                    self.mount_sidebar_to_screen()

                self.toggle_sidebar()    

        elif event.key == "ctrl+q" and self.store["argument_parser_type"] == "dir":
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

        #### block key <aa>
        elif event.key == "a" and self.typed_key == "":
            if self.focused_main_editor is False:
                self.typed_key = "a"
                self.typed_key_timer = time.time()
        
        # <aa> append file
        elif event.key == "a" and self.typed_key == "a" and self.store["argument_parser_type"] == "dir": 
            if time.time() - self.typed_key_timer > 3:
                self.reset_typed_key()
            else:
                sidebar = self.query_one(Sidebar)
                highlighted_content = self.query("DirectoryContentText")[sidebar.viewing_id - 1]
                sidebar.mount_input(highlighted_content=highlighted_content) 
                self.typed_key = ""
        #### end block key <aa>

        ### black key <dd>
        elif event.key == "d" and self.typed_key == "":
            if self.focused_main_editor is False:
                self.typed_key = "d"
                self.typed_key_timer = time.time()
        elif event.key == "d" and self.typed_key == "d" and self.store["argument_parser_type"] == "dir":
            if time.time() - self.typed_key_timer > 3:
                self.reset_typed_key()
            else:
                self.typed_key = ""
                sidebar = self.query_one(Sidebar)
                content_to_delete = self.query("DirectoryContentText")[sidebar.viewing_id - 1]  

                def after_delete_action(selected_content=None, editor=self) -> None:
                    if selected_content is not None:
                        sidebar = editor.query_one("Sidebar")
                        c_path = selected_content.content_path
                        c_type = selected_content.content_type
                        project_root = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")["project_root"]
                        in_project_root = False

                        if c_type == "file":
                            if os.path.dirname(c_path) == project_root:
                                in_project_root = True
                        elif c_type == "dir":
                            if str(Path(c_path).parent) == project_root:
                                in_project_root = True

                        # if it's in project root need to change dir_tree and remount listview
                        if in_project_root:
                            for (index, content) in enumerate(sidebar.dir_tree):
                                if selected_content.content_id == index + 1:
                                    # if it's a directory and state is open, close the directory first
                                    if sidebar.content_states[f"content_{index+1}"] == "open":
                                        sidebar.close_directory(
                                            sidebar.query("DirectoryContentText")[sidebar.viewing_id - 1]
                                        )

                                    sidebar.dir_tree.remove(content)
                                    sidebar.utils.handle_re_mount_listview()
                                    break
                        # if it's not in project root, close the parent dir and reopen it
                        # close_directory and open_directory will handle updating dir_tree and remount listview
                        else:
                            for content in sidebar.query("DirectoryContentText"):
                                if content.content_path == str(Path(c_path).parent):
                                    sidebar.close_directory(content)
                                    sidebar.open_directory(content)
                                    break
  
                self.app.push_screen(DeleteDialog(content_to_delete=content_to_delete), after_delete_action)
    
        elif event.key == "enter":
            if self.focused_main_editor:
                pass
            else:
                sidebar = self.query_one(Sidebar)
                selected_content_index = sidebar.viewing_id - 1
                selected_content = self.query("DirectoryContentText")[selected_content_index]

                # enter on files
                if selected_content.content_type == "file":
                    sidebar.select_file(selected_content=selected_content)
                    self.handle_switching_focus()
                
                # enter on directories
                else:
                    sidebar.select_directory(selected_dir=selected_content)
                    sidebar.focus()
                    self.focused_main_editor = False

        elif event.key == "escape":
            self.typed_key = ""
