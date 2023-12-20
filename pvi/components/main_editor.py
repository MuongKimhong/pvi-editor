from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static
from textual.messages import Message
from textual import log, events


class MainEditor(Container, can_focus=True):
    def compose(self) -> ComposeResult:
        yield Static("Main editor here")

    def on_focus(self, event: events.Focus) -> None:
        log("Main editor is focused")

    