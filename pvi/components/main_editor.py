from textual.widgets.text_area import Selection
from textual.widgets import Static, TextArea
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.messages import Message
from textual.widget import Widget
from textual import log, events

from key_binding import KeyBindingInNormalMode, KeyBindingInSelectionMode
from components.welcome_text import WelcomeText
from components.text_area import PviTextArea
from syntax_highlighting import Syntax
from components.footer import Footer
from components.header import Header
from utils import read_ini_file


class MainEditor(Container, can_focus=True):
    def __init__(self) -> None:
        self.editing_mode = "normal"
        self.content_loaded = False # True if user open a file to edit
        self.selection_start = None
        self.copied_text = ""
        self.selection_mode_keybinding = KeyBindingInSelectionMode(self)
        self.normal_mode_keybinding = KeyBindingInNormalMode(self)

        '''
        typed_key variable is used for 2 keys binding operations. Including:
        - <dd> delete the entire line
        - <sa> select all
        - <sl> select the entire line
        - <yy> copy the entire line
        - <af> append new file in sidebar
        - <ad> append new directory in sidebar
        - <gt> go to top of document
        - <gb> go to bottom of document
        '''
        self.typed_key = ""  
        self.typed_key_timer: float | None = None # time when typed_key is assigned
        super().__init__()

    def compose(self) -> ComposeResult:
        store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")

        if store["argument_parser_type"] == "dir":
            yield WelcomeText(id="welcome-text")
            yield Header(id="header")
        else:
            with open(store["editing_path"], "r") as file:
                self.handle_load_content_to_textarea(
                    file_content=file.read(),
                    file_name=store["editing_path"].split("/")[-1]
                )
                
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
        theme = syntax.my_theme()

        try:
            text_area = self.app.query_one("#pvi-text-area")
            text_area.load_text(file_content)
            self.app.query_one("Footer").update_total_line(text_area.document.line_count)
        except NoMatches:
            text_area = PviTextArea(file_content, id="pvi-text-area")
            self.mount(text_area)
            text_area.scroll_visible()
            text_area.register_theme(theme) 
            text_area.register_theme(syntax.my_theme_insert_mode())
            text_area.theme = "my_theme" 
            
        text_area.language = "python" # set language to python no matter what's file type

        # if file type supp by pvi
        if tree_sitter_language is not None:
            if syntax.textual_spp(file_name) is False:
                hl_query = syntax.get_highlight_query(language=language)
                text_area.register_language(tree_sitter_language, hl_query)

            text_area.language = language
        
        # this is the last thing user can undo 
        text_area.old_document = text_area.document.text 
        text_area.undo_states.append({"text": text_area.document.text, "cursor": text_area.cursor_location})

    def handle_load_content_to_textarea(self, file_content: str, file_name: str) -> None:
        self.content_loaded = True
        self.remove_welcome_text()
        self.load_file_content_to_textarea(file_content, file_name)

    def reset_typed_key(self) -> None:
        self.typed_key = ""
        self.typed_key_timer = None

    def on_focus(self, event: events.Focus) -> None:
        self.editing_mode = "normal"

    def on_key(self, event: events.Key) -> None:
        if self.editing_mode == "normal":
            if event.character == ":": # give focus to footer and handle command execution
                self.app.query_one("#footer").query_one("#command-input").focus()
            
            if self.content_loaded:
                self.normal_mode_keybinding.handle_key_binding(key_event=event)

        elif self.editing_mode == "selection":
            if self.content_loaded:
                self.selection_mode_keybinding.handle_key_binding(key_event=event)
