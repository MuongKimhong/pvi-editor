from textual.app import ComposeResult
from textual.widgets import Static


class Sidebar(Static):
    def compose(self) -> ComposeResult:
        yield Static("", id="sidebar")

     