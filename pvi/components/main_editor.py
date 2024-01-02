from textual.widgets.text_area import Selection
from textual.widgets import Static, TextArea
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.messages import Message
from textual.widget import Widget
from textual import log, events

from utils import read_ini_file, KeyBindingInSelectionMode, KeyBindingInNormalMode
from components.welcome_text import WelcomeText
from components.text_area import PviTextArea
from components.footer import Footer
from syntax_highlighting import Syntax


class MainEditor(Container, can_focus=True):
    def __init__(self) -> None:
        self.editing_mode = "normal"
        self.content_loaded = False # True if user open a file to edit
        self.typed_key = ""
        self.selection_start = None
        self.copied_text = ""

        self.selection_mode_keybinding = KeyBindingInSelectionMode(self)
        self.normal_mode_keybinding = KeyBindingInNormalMode(self)
        super().__init__()

    def compose(self) -> ComposeResult:
        if read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")["editing_type"] == "dir":
            yield WelcomeText(id="welcome-text")
        
        yield Footer(id="footer")
    
    def remove_welcome_text(self) -> None:
        try:
            self.query_one("#welcome-text").remove()
        except NoMatches:
            pass

    def load_file_content_to_textarea(self, file_content: str, file_name: str) -> None:
        syntax = Syntax()
        tree_sitter_language = syntax.file_type_to_tree_sitter_language(file_name=file_name)
        language = syntax.file_type_to_language(file_name=file_name)

        try:
            text_area = self.app.query_one("#pvi-text-area")
            text_area.load_text(file_content)
        except NoMatches:
            text_area = PviTextArea(file_content, id="pvi-text-area")
            self.mount(text_area)
            text_area.scroll_visible()

        if tree_sitter_language is not None:
            if syntax.textual_spp(file_name) is False:
                hl_query = syntax.get_highlight_query(language=language)
                text_area.register_language(tree_sitter_language, hl_query)

            text_area.language = language

    def handle_load_content_to_textarea(self, file_content: str, file_name: str) -> None:
        self.content_loaded = True
        self.remove_welcome_text()
        self.load_file_content_to_textarea(file_content, file_name)

    def on_focus(self, event: events.Focus) -> None:
        self.editing_mode = "normal"

    def on_key(self, event: events.Key) -> None:
        if self.editing_mode == "normal":
            if event.character == ":": # give focus to footer and handle command execution
                self.app.query_one("#footer").focus()
            
            if self.content_loaded:
                self.normal_mode_keybinding.handle_key_binding(key_event=event)

        elif self.editing_mode == "selection":
            if self.content_loaded:
                self.selection_mode_keybinding.handle_key_binding(key_event=event)
