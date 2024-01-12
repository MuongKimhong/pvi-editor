from textual.widgets import TextArea, Static, ListView, ListItem
from textual.containers import Container
from textual.css.query import NoMatches
from textual.geometry import Offset
from textual import events, log

from autocomplete import AutoComplete
import time


class SuggestionPanel(Container):
    DEFAULT_CSS = """
    SuggestionPanel {
        layer: above;
        width: 35;
        content-align: center middle;
        background: grey;
        color: white
    }
    """

    def __init__(self, listview: ListView) -> None:
        self.listview = listview
        super().__init__()

    def compose(self):
        yield self.listview

    def update_height(self, height: int) -> None:
        self.styles.height = height

    def update_offset(self, offset: Offset) -> None:
        self.styles.offset = offset


class PviTextArea(TextArea):
    autocomplete_symbol = ['{', '[', '(']
    autocomplete_engine = None
    suggestion_words = []

    change_occurs = 0 # increase 1 every changes
    change_updates = 0 # update to number of occurs every 10 changes

    # combination of keypress. return to empty string whenever user press space key
    typing_word = ""

    DEFAULT_CSS = """
    PviTextArea {
        layers: above;
    } 
    """

    def handle_autocomplete_symbol(self, character) -> None:
        match character:
            case "{":
                text = "}"
            case "[":
                text = "]"
            case "(":
                text = ")"
        
        replacement_line = self.document.get_line(self.cursor_location[0])
        replacement_text = replacement_line[self.cursor_location[1]:]

        if replacement_text == "":
            self.replace(
                insert=text,
                start=self.cursor_location,
                end=(self.cursor_location[0], self.cursor_location[1] + 1)
            )
        else:
            self.replace(
                insert=text + replacement_text, 
                start=self.cursor_location,
                end=self.get_cursor_line_end_location(),
            )

    def remove_suggestion_from_dom(self) -> None:
        try:
            self.query_one(SuggestionPanel).remove()
        except NoMatches:
            pass

    def on_focus(self, event: events.Focus) -> None:
        self.theme = "my_theme_insert_mode"

        if self.autocomplete_engine is None:
            self.autocomplete_engine = AutoComplete(language=self.language)
            self.suggestion_words = self.autocomplete_engine.get_suggestion(self.document.text)

    def on_blur(self, event: events.Blur) -> None:
        self.theme = "my_theme"
        self.remove_suggestion_from_dom()

    # update the suggestion words every 10 changes
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.change_occurs = self.change_occurs + 1

        if (self.change_occurs - self.change_updates) >= 10:
            self.suggestion_words = self.autocomplete_engine.get_suggestion(
                event.text_area.document.text
            )
            self.change_updates = self.change_occurs

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normal--") 

        elif event.character in self.autocomplete_symbol:
            self.handle_autocomplete_symbol(character=event.character)
        
        else:
            if (event.is_printable) and (event.key != "space"):
                self.typing_word = self.typing_word + event.character
            elif (event.key == "backspace") and (self.typing_word != ""):
                self.typing_word = self.typing_word[:-1] 
            elif event.key == "space":
                self.typing_word = "" 

            matched_words = []

            for word in self.suggestion_words:
                if (len(self.typing_word) > 0) and (self.typing_word.lower() in word.lower()):
                    matched_words.append(word)

            self.remove_suggestion_from_dom()

            if len(matched_words) > 0:
                suggestion_panel = SuggestionPanel(listview=ListView(*[]))
                self.mount(suggestion_panel)
                suggestion_panel.scroll_visible()

                suggestion_panel = self.query_one(SuggestionPanel) 
                suggestion_panel.update_height(height=len(matched_words))
                suggestion_panel.update_offset(
                    offset=(self.cursor_location[1] + 4, self.cursor_location[0] + 1)
                )
                for word in matched_words:
                    suggestion_panel.listview.append(ListItem(Static(word)))
