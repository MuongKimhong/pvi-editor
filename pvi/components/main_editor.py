from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, TextArea
from textual.messages import Message
from textual.widget import Widget
from textual import log, events

from components.welcome_text import WelcomeText
from utils import read_store_ini_file


class MainEditor(Container, can_focus=True):
    def __init__(self) -> None:
        self.editing_mode = "normal"
        super().__init__()

    def compose(self) -> ComposeResult:
        if read_store_ini_file(section_name="WorkingDirectory")["editing_type"] == "dir":
            yield WelcomeText(id="welcome-text")

    def on_focus(self, event: events.Focus) -> None:
        log("Main editor is focused")
        self.editing_mode = "normal"

    def on_key(self, event: events.Key) -> None:
        if self.editing_mode == "normal":
            if event.key == "j":
                self.query_one("#pvi-text-area").action_cursor_down()
            elif event.key == "k":
                self.query_one("#pvi-text-area").action_cursor_up()
            elif event.key == "l":
                self.query_one("#pvi-text-area").action_cursor_right()
            elif event.key == "h":
                self.query_one("#pvi-text-area").action_cursor_left()
            elif event.key == "i": # change to insert mode
                self.editing_mode = "insert"
                self.query_one("#pvi-text-area").focus()
