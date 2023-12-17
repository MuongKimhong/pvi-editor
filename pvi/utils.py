from pathlib import Path
import configparser


def get_pvi_root() -> Path:
    return Path(__file__).parent.parent


def read_ini_file(section_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read("store/stores.ini")
    return config[section_name] 


def update_ini_file(section_name: str, section_data: dict) -> None:
    config = configparser.ConfigParser()
    config[section_name].update(section_data)

    with open("store/stores.ini", "w") as configfile:
        config.write(configfile)
