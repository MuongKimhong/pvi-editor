from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, TextArea
from textual.widgets.text_area import Selection
from textual.css.query import NoMatches
from textual.messages import Message
from textual.widget import Widget
from textual import log, events

from components.welcome_text import WelcomeText
from components.text_area import PviTextArea
from components.footer import Footer
from utils import read_store_ini_file, KeyBindingInSelectionMode


class MainEditor(Container, can_focus=True):
    def __init__(self) -> None:
        self.editing_mode = "normal"
        self.content_loaded = False # True if user open a file to edit
        self.typed_key = ""
        self.selection_start = None
        self.selection_mode_keybinding = KeyBindingInSelectionMode(self)
        super().__init__()

    def compose(self) -> ComposeResult:
        if read_store_ini_file(section_name="WorkingDirectory")["editing_type"] == "dir":
            yield WelcomeText(id="welcome-text")
        
        yield Footer(id="footer")
    
    def remove_welcome_text(self) -> None:
        try:
            self.query_one("#welcome-text").remove()
        except NoMatches:
            pass

    def load_file_content_to_textarea(self, file_content: str) -> None:
        try:
            text_area = self.app.query_one("#pvi-text-area")
            text_area.load_text(file_content)
        except NoMatches:
            text_area = PviTextArea(file_content, id="pvi-text-area")
            self.mount(text_area)
            text_area.scroll_visible()

    def handle_load_content_to_textarea(self, file_content: str) -> None:
        self.content_loaded = True
        self.remove_welcome_text()
        self.load_file_content_to_textarea(file_content)

    def on_focus(self, event: events.Focus) -> None:
        self.editing_mode = "normal"

    def on_key(self, event: events.Key) -> None:
        if self.editing_mode == "normal":
            if event.character == ":":
                self.app.query_one("#footer").focus()
            
            if self.content_loaded:
                text_area = self.query_one("#pvi-text-area")

                if event.key == "j":
                    text_area.action_cursor_down()
                elif event.key == "k":
                    text_area.action_cursor_up()
                elif event.key == "l":
                    text_area.action_cursor_right()
                elif event.key == "h":
                    text_area.action_cursor_left()
                elif event.key == "i": # change to insert mode
                    self.editing_mode = "insert"
                    self.app.query_one("#footer").change_value(value="--insert--")
                    text_area.focus()

                elif event.key == "d" and self.typed_key == "":
                    self.typed_key = self.typed_key + event.key
                elif event.key == "d" and self.typed_key == "d": # combination of dd, delete a line
                    text_area.action_delete_line()
                    self.typed_key = ""

                elif event.key == "v": # start selection
                    self.editing_mode = "selection"
                    self.app.query_one("#footer").change_value(value="--selection--")
                    self.selection_start = text_area.cursor_location
                    text_area.selection = Selection(start=text_area.cursor_location, end=text_area.cursor_location)

        elif self.editing_mode == "selection":
            if self.content_loaded:
                self.selection_mode_keybinding.handle_key_binding(key_event=event)
