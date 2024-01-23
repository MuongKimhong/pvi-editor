from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static
from textual import events

from utils import read_ini_file, get_pvi_root


class Header(Container):
    with open(f"{get_pvi_root()}/pvi/styles/header_style.tcss", "r") as file:
        DEFAULT_CSS = file.read()

    def compose(self) -> ComposeResult:
        yield Static("PVI Editor", id="header-text")

