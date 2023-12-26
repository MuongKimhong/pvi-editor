from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events, log

from utils import read_setting_ini_file


class Footer(Input, can_focus=True):
    def set_style(self) -> None:
        style = read_setting_ini_file(section_name="Footer")
        self.styles.dock = "bottom" #  can't be changed
        self.styles.width = "100%" # can't be changed
        self.styles.height = int(style["height"])
        self.styles.background = f"#{style['background_color']}"
        self.styles.color = style["text_color"]
        self.styles.border = ("hidden", "grey")
        
    def on_mount(self, event: events.Mount) -> None:
        self.value = "--normal--"
        self.set_style()

    def on_focus(self, event: events.Focus) -> None:
        self.value = ":"

    def change_value(self, value: str) -> None:
        self.value = value

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            log("escape key is pressed")
            self.value = "--normal--"
            self.blur()
            self.app.query_one("MainEditor").focus()
        elif event.key == "enter": # execute command
            if self.value == ":q":
                self.app.exit()

