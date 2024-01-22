from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static

from utils import get_pvi_root


class WelcomeText(Container):
    with open(f"{get_pvi_root()}/pvi/styles/welcome_text_style.tcss", "r") as file:
        DEFAULT_CSS = file.read()

    def compose(self) -> ComposeResult:
        yield Static("Welcome to PVI - Python Vim Editor\n", id="welcome")
        yield Static("Happy Coding!", id="happy-coding")