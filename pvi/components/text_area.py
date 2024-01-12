from textual.widgets import TextArea, Static, ListView, ListItem
from textual.css.query import NoMatches
from textual.geometry import Offset
from textual import events, log

from autocomplete import AutoComplete
import time


class PviTextArea(TextArea):
    autocomplete_symbol = ['{', '[', '(']
    autocomplete_engine = None
    suggestion_words = []
    suggestion_listview = ListView(*[], id="suggestion-listview")

    # update the suggestion words every 10 new lines   
    UPDATE_SUGGESTION_INTERVAL = 10
    change_occurs = 0 # increase 1 every changes
    change_updates = 0 # update to number of occurs every 10 changes

    # combination of keypress. return to empty string whenever user press space key
    typing_word = ""

    DEFAULT_CSS = """
    PviTextArea {
        layers: above;
    } 
    """

    def set_suggestion_listview_style(self) -> None:
        self.suggestion_listview.styles.layer = "above"
        self.suggestion_listview.styles.width = 40
        self.suggestion_listview.styles.content_align = ("center", "middle")
        self.suggestion_listview.styles.background = "grey"
        self.suggestion_listview.styles.color = "white"

    def update_suggestion_listview_offset(self, offset: Offset) -> None:
        self.suggestion_listview.styles.offset = offset

    def update_suggestion_listview_height(self, height: int) -> None:
        self.suggestion_listview.styles.height = height

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

        if self.autocomplete_engine is None:
            self.autocomplete_engine = AutoComplete(language=self.language)
            self.suggestion_words = self.autocomplete_engine.get_suggestion(self.document.text)

        self.set_suggestion_listview_style()

    def on_blur(self, event: events.Blur) -> None:
        self.theme = "my_theme"
        
        try:
            self.query_one("#suggestion-listview").styles.visibility = "hidden"
        except NoMatches:
            pass

    # update the suggestion words every 10 changes
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.change_occurs = self.change_occurs + 1

        if (self.change_occurs - self.change_updates) >= 10:
            self.suggestion_words = self.autocomplete_engine.get_suggestion(
                event.text_area.document.text
            )
            self.change_updates = self.change_occurs
            self.query_one("#suggestion-listview").remove()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normal--") 

        elif event.character in self.autocomplete_symbol:
            self.handle_autocomplete_symbol(character=event.character)
        
        else:
            if event.is_printable or event.key == "backspace":

                if event.is_printable:
                    self.typing_word = self.typing_word + event.character

                if event.key == "backspace":
                    self.typing_word = self.typing_word[:-1]
                    self.query_one("#suggestion-listview").styles.visibility = "visible"

                matched_words = [word for word in self.suggestion_words if self.typing_word in word]

                if len(matched_words) > 0:
                    try:
                        self.query_one("#suggestion-listview")
                    except NoMatches:
                        self.mount(self.suggestion_listview)
                        self.suggestion_listview.scroll_visible()
                    
                    self.update_suggestion_listview_height(len(matched_words))
                    self.update_suggestion_listview_offset(
                        (self.cursor_location[1] + 5, self.cursor_location[0] + 1)
                    )

                    for word in matched_words:
                        self.suggestion_listview.append(ListItem(Static(word)))
                else:
                    try:
                        self.query_one("#suggestion-listview").styles.visibility = "hidden"
                    except NoMatches:
                        pass

            # elif event.key == "backspace":
            #     pass