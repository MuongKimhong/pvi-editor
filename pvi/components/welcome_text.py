from textual.widgets import Static, Label
from textual.containers import Container
from textual.app import ComposeResult


class WelcomeText(Container):
    CSS_PATH = "../styles/style.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Welcome to PVI - Python Vim Editor\n", id="welcome")
        yield Label("Happy Coding!", id="happy-coding")