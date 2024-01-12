from textual.widgets import TextArea, Static, ListView, ListItem
from textual import events, log

from autocomplete import AutoComplete
import time


class PviTextArea(TextArea):
    autocomplete_symbol = ['{', '[', '(']
    autocomplete_engine = None
    suggestion_words = []

    
    # update the suggestion words every 10 new lines   
    UPDATE_SUGGESTION_INTERVAL = 10
    start_interval_line_index = 0

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

    def on_focus(self, event: events.Focus) -> None:
        self.theme = "my_theme_insert_mode"
        self.autocomplete_engine = AutoComplete(language=self.language)
        self.suggestion_words = self.autocomplete_engine.get_suggestion(self.document.text)
        self.start_interval_line_index = 0

    def on_blur(self, event: events.Blur) -> None:
        self.theme = "my_theme"

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normal--") 

        elif event.character in self.autocomplete_symbol:
            self.handle_autocomplete_symbol(character=event.character) 

        
 
        elif event.key == "s":
            listview = ListView(*[], id="suggestion-listview")
            listview.styles.layer = "above"
            listview.styles.width = 50
            listview.styles.height = 10
            listview.styles.content_align = ("center", "middle")
            listview.styles.offset = (13, 6)
            listview.styles.background = "yellow"
            listview.styles.color = "white"

            for word in self.suggestion_words:
                static = Static(word, id="text")
                static.styles.width = 30
                static.styles.height = 1
                static.styles.content_align = ("center", "middle")
                listview.append(
                    ListItem(static)
                )
                
            self.mount(listview)
            listview.scroll_visible()