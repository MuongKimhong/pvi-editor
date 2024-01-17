from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static
from textual import events

from utils import read_ini_file


class Header(Container):
    DEFAULT_CSS = """
    Header {
        align: center top; 
    }
    Header #header-text {
        text-align: center;
    }
    """

    def set_style(self) -> None:
        style = read_ini_file(file_name="settings.ini", section_name="Header")
        self.styles.dock = "top" #  can't be changed
        self.styles.width = "100%" # can't be changed
        self.styles.height = int(style["height"])
        self.styles.background = f"#{style['background_color']}"
        self.styles.color = style["text_color"]
        self.styles.border = ("hidden", "grey")

    def compose(self) -> ComposeResult:
        yield Static("PVI Editor", id="header-text")

    def on_mount(self, event: events.Mount) -> None:
        self.set_style() 
