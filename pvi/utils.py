from textual.widgets.text_area import Selection
from textual.messages import Message
from textual import log

from pathlib import Path
import configparser

def get_pvi_root() -> Path:
    return Path(__file__).parent.parent


def read_store_ini_file(section_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read(f"{get_pvi_root()}/pvi/store/stores.ini")
    return config[section_name] 


def update_store_ini_file(section_name: str, section_data: dict) -> None:
    config = configparser.ConfigParser()
    config.read(f"{get_pvi_root()}/pvi/store/stores.ini")
    config[section_name].update(section_data)

    with open(f"{get_pvi_root()}/pvi/store/stores.ini", "w") as configfile:
        config.write(configfile)


def read_setting_ini_file(section_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read(f"{get_pvi_root()}/pvi/store/settings.ini")
    return config[section_name]


def update_setting_ini_file(section_name: str, section_data: dict) -> None:
    config = configparser.ConfigParser()
    config.read(f"{get_pvi_root()}/pvi/store/settings.ini")
    config[section_name].update(section_data)

    with open(f"{get_pvi_root()}/pvi/store/settings.ini", "w") as configfile:
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
                text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)

            case "k":
                text_area.action_cursor_up()
                text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)                

            case "l":
                text_area.action_cursor_right()
                text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)
            
            case "h":
                text_area.action_cursor_left()
                text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location) 
            
            case "d":
                text_area.delete(start=self.main_editor.selection_start, end=text_area.cursor_location)
                self.cancel_selection(text_area)
            
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
                text_area.action_cursor_line_end()
                start, end = text_area.selection
                text_area.replace("\n", start, end, maintain_selection_offset=False)
                self.enter_insert_mode(text_area)
            case "b":
                text_area.action_cursor_word_left()
            case "w":
                text_area.action_cursor_word_right()

        if key_event.key == "d" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = self.main_editor.typed_key + key_event.key

        elif key_event.key == "d" and self.main_editor.typed_key == "d": # combination of dd, delete a line
            text_area.action_delete_line()
            self.main_editor.typed_key = ""