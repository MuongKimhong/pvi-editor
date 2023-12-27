from pathlib import Path
import configparser

from textual.widgets.text_area import Selection
from textual.messages import Message
from textual import log


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

        if key_event.key == "j":
            text_area.action_cursor_down()
            text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)

        elif key_event.key == "k":
            text_area.action_cursor_up()
            text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)

        elif key_event.key == "l":
            text_area.action_cursor_right()
            text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)

        elif key_event.key == "h":
            text_area.action_cursor_left()
            text_area.selection = Selection(start=self.main_editor.selection_start, end=text_area.cursor_location)

        elif key_event.key == "d":
            text_area.delete(start=self.main_editor.selection_start, end=text_area.cursor_location)
            self.cancel_selection(text_area)

        elif key_event.key == "escape": # cancel selection
            self.cancel_selection(text_area)