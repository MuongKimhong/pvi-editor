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


class KeyBindingInSelectionMode:
    def __init__(self, main_editor):
        self.main_editor = main_editor

    def cancel_selection(self, text_area) -> None:
        self.main_editor.selection_start = None
        self.main_editor.editing_mode = "normal"
        self.main_editor.app.query_one("#footer").change_value(value="--normal--")
        text_area.selection = Selection(start=text_area.cursor_location, end=text_area.cursor_location)

    def handle_key_binding(self, key_event) -> None:
        text_area = self.main_editor.query_one("#pvi-text-area")  

        match key_event.key:
            case "j":
                text_area.action_cursor_down()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "k":
                text_area.action_cursor_up()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )                
            case "l":
                text_area.action_cursor_right()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                ) 
            case "h":
                text_area.action_cursor_left()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                ) 
            case "d":
                text_area.delete(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
                self.cancel_selection(text_area)
            
            case "w":
                text_area.action_cursor_word_right()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "b":
                text_area.action_cursor_word_left()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "A": #upper a
                text_area.action_cursor_line_end()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "I": # upper i
                text_area.action_cursor_line_start()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "y": # copy the selected text
                self.main_editor.copied_text = text_area.selected_text
           
            case "escape":
                self.cancel_selection(text_area)


class KeyBindingInNormalMode:
    def __init__(self, main_editor):
        self.main_editor = main_editor

    def enter_insert_mode(self, text_area) -> None:
        self.main_editor.editing_mode = "insert"
        self.main_editor.app.query_one("#footer").change_value(value="--insert--")
        text_area.focus()

    def enter_selection_mode(self, text_area) -> None:
        self.main_editor.editing_mode = "selection"
        self.main_editor.app.query_one("#footer").change_value(value="--selection--")
        self.main_editor.selection_start = text_area.cursor_location
        text_area.selection = Selection(start=text_area.cursor_location, end=text_area.cursor_location)

    def create_new_line(self, text_area) -> None:
        text_area.action_cursor_line_end()
        start, end = text_area.selection
        text_area.replace("\n", start, end, maintain_selection_offset=False)

    def handle_key_binding(self, key_event) -> None:
        text_area = self.main_editor.query_one("#pvi-text-area")

        match key_event.key:
            case "j":
                text_area.action_cursor_down()
            case "k":
                text_area.action_cursor_up()
            case "l":
                text_area.action_cursor_right()
            case "h":
                text_area.action_cursor_left()
            case "i":
                self.enter_insert_mode(text_area)
            case "v":
                self.enter_selection_mode(text_area)
            case "o": 
                self.create_new_line(text_area)
                self.enter_insert_mode(text_area)
            case "b":
                text_area.action_cursor_word_left()
            case "w":
                text_area.action_cursor_word_right()
            case "A": # upper a
                text_area.action_cursor_line_end()
                self.enter_insert_mode(text_area)
            case "I": # upper i
                text_area.action_cursor_line_start()
                self.enter_insert_mode(text_area)
            case "p": # paste
                if self.main_editor.copied_text != "":
                    self.create_new_line(text_area)
                    text_area.action_cursor_line_end()
                    start, end = text_area.selection
                    text_area.replace(self.main_editor.copied_text, start, end, maintain_selection_offset=False)
                    self.main_editor.copied_text = ""

        if key_event.key == "d" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = self.main_editor.typed_key + key_event.key

        elif key_event.key == "d" and self.main_editor.typed_key == "d": # combination of dd, copy and delete a line
            text_area.action_select_line()
            self.main_editor.copied_text = text_area.selected_text
            text_area.action_delete_line()
            self.main_editor.typed_key = ""

        elif key_event.key == "s" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = self.main_editor.typed_key + key_event.key
        
        elif key_event.key == "a" and self.main_editor.typed_key == "s":
            self.main_editor.typed_key = ""
            self.enter_selection_mode(text_area)
            text_area.action_select_all()

        elif key_event.key == "y" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = self.main_editor.typed_key + key_event.key

        elif key_event.key == "y" and self.main_editor.typed_key == "y": # yy, copy the entire line
            text_area.action_select_line()
            self.main_editor.copied_text = text_area.selected_text


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
    def content_as_dict(self, c_type: str, content: str, layer_level: int) -> dict:
        return {
            "type": c_type,
            "content": content,
            "layer_level": layer_level
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
