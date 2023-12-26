from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events, log

from utils import read_setting_ini_file



# style = read_setting_ini_file(section_name="Footer")
        # self.styles.dock = "bottom" #  can't be changed
        # self.styles.width = "100%" # can't be changed
        # self.styles.height = int(style["height"])
        # self.styles.background = f"#{style['background_color']}"
        # self.styles.color = style["text_color"]