from pathlib import Path
import configparser

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


# event Read File. Called when user open a file in sidebar
class Read(Message):
    def __init__(self, file_content: str) -> None:
        self.file_content = file_content
        super().__init__()
