from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, TextArea
from textual.messages import Message
from textual import log, events

from components.welcome_text import WelcomeText
from utils import read_store_ini_file


class MainEditor(Container, can_focus=True):
    def compose(self) -> ComposeResult:
        if read_store_ini_file(section_name="WorkingDirectory")["editing_type"] == "dir":
            yield WelcomeText(id="welcome-text")

    def on_focus(self, event: events.Focus) -> None:
        log("Main editor is focused")
