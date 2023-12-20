from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, TextArea
from textual.messages import Message
from textual import log, events

from .utils import Read


class MainEditor(Container, can_focus=True):
    def compose(self) -> ComposeResult:
        yield Static("Main editor here")

    def on_focus(self, event: events.Focus) -> None:
        log("Main editor is focused")

    # called when user read file content from sidebar
    def on_read(self, event: ReadFile) -> None:
        pass 