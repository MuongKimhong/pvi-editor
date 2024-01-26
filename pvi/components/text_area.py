from textual.widgets import TextArea, Static, ListView, ListItem
from textual.containers import Container
from textual.css.query import NoMatches
from textual.geometry import Offset
from textual import events, log

from autocomplete import AutoComplete
import time


class SuggestionPanel(Container, can_focus=True):
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

    # auto indent when user presses key <enter> if user type symbol below
    auto_indentation_symbol = ["{", "[", "(", ":"] 
    auto_indent = False # auto indent whenever True
    line_start_location_before_indent: tuple | None = None

    change_occurs = 0 # increase 1 every changes
    change_updates = 0 # update to number of occurs every 10 changes

    # combination of keypress. return to empty string whenever user press space key
    typing_word = ""
    suggestion_panel_focused = False

    # track document, cursor before undo operation
    old_document = ""
    old_cursor_location = None
    undo_states = []

    DEFAULT_CSS = """
    PviTextArea {
        layers: above;
    } 
    """

    def handle_autocomplete_symbol(self, character: str) -> None:
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
            self.suggestion_panel_focused = False
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

    def on_mount(self, event: events.Mount) -> None:
        self.app.query_one("Footer").update_total_line(self.document.line_count)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if (self.auto_indent) and (self.line_start_location_before_indent is not None):
            event.text_area.move_cursor(self.line_start_location_before_indent)
            event.text_area.action_cursor_line_end()
            self.insert(
                text="\n", 
                location=(self.cursor_location[0], self.cursor_location[1] + 1)
            )
            self.insert(
                text=" " * self._find_columns_to_next_tab_stop(),
                location=self.cursor_location
            ) 
            self.auto_indent = False
            self.line_start_location_before_indent = None

        self.change_occurs = self.change_occurs + 1

        # update the suggestion words every 10 changes
        if (self.change_occurs - self.change_updates) >= 10:
            self.suggestion_words = self.autocomplete_engine.get_suggestion(
                event.text_area.document.text
            )
            self.change_updates = self.change_occurs

        # every 5 document length differrent, update the undo states
        if ((len(event.text_area.document.text) - len(self.old_document) >= 5) or
            (len(self.old_document) - len(event.text_area.document.text) >= 5)):

            if len(self.undo_states) >= 1:
                self.undo_states.insert(0, {"text": event.text_area.document.text, "cursor": self.cursor_location})
                self.old_document = event.text_area.document.text

        footer = self.app.query_one("Footer")
        footer.update_current_line(self.cursor_location[0] + 1)        
        footer.update_total_line(self.document.line_count)
        
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        selected_word = str(event.item._nodes[0].renderable)
        replacement_line = self.document.get_line(self.cursor_location[0])
        replacement_text = replacement_line[self.cursor_location[1]:]
         
        if replacement_text == "":
            insert_word = selected_word
            start = (self.cursor_location[0], self.cursor_location[1] - len(self.typing_word))
            end = (self.cursor_location[0], self.cursor_location[1] + len(selected_word))
            cursor_location = (
                self.cursor_location[0], 
                self.cursor_location[1] + len(selected_word)
            )
        else:
            insert_word = selected_word + replacement_text
            start = (self.cursor_location[0], self.cursor_location[1] - len(self.typing_word))
            end = self.get_cursor_line_end_location()
            cursor_location = (
                self.cursor_location[0], 
                self.cursor_location[1] + len(selected_word) - len(self.typing_word)
            )
        self.replace(insert=insert_word, start=start, end=end)
        self.move_cursor(cursor_location)
        self.typing_word = ""
        self.remove_suggestion_from_dom()

    def on_key(self, event: events.Key) -> None:
        footer = self.app.query_one("Footer")

        if event.character in self.autocomplete_symbol:
            self.handle_autocomplete_symbol(character=event.character)

        if event.character in self.auto_indentation_symbol:
            self.auto_indent = True
        elif (event.key != "enter") and (event.character not in self.auto_indentation_symbol):
            self.auto_indent = False 
            self.line_start_location_before_indent = None

        if event.key == "escape":
            self.blur()
            self.app.query_one("Footer").update_input(value="-- NORMAL --") 
        
        else:
            if (event.is_printable) and (event.key != "space"):
                self.typing_word = self.typing_word + event.character
                self.suggestion_panel_focused = False
            elif (event.key == "backspace") and (self.typing_word != ""):
                self.typing_word = self.typing_word[:-1] 
                self.suggestion_panel_focused = False
            elif event.key == "space":
                self.typing_word = "" 
                self.suggestion_panel_focused = False
            elif (event.key == "enter") and (self.suggestion_panel_focused is False):
                self.typing_word = "" 
                self.line_start_location_before_indent = self.get_cursor_line_start_location()

            elif event.key == "down":
                try:
                    self.query_one(SuggestionPanel).listview.action_cursor_down()
                    self.action_cursor_up()
                    self.suggestion_panel_focused = True
                except NoMatches:
                    pass
            elif event.key == "up":
                try:
                    self.query_one(SuggestionPanel).listview.action_cursor_up()
                    self.action_cursor_down()
                    self.suggestion_panel_focused = True
                except NoMatches:
                    pass
            elif (event.key == "enter") and (self.suggestion_panel_focused is True):
                event.prevent_default()
                self.query_one(SuggestionPanel).listview.action_select_cursor()

            if self.suggestion_panel_focused is False:
                matched_words = []

                for word in self.suggestion_words:
                    if (len(self.typing_word) > 0) and (self.typing_word.lower() in word.lower()):
                        matched_words.append(word)

                self.remove_suggestion_from_dom()

                if len(matched_words) > 0:
                    suggestion_panel = SuggestionPanel(listview=ListView(*[]))
                    self.mount(suggestion_panel)
                    suggestion_panel.scroll_visible()
                    self.suggestion_panel_focused = True

                    suggestion_panel = self.query_one(SuggestionPanel) 
                    suggestion_panel.update_height(height=len(matched_words))
                    suggestion_panel.update_offset(
                        offset=(self.cursor_location[1] + 4, self.cursor_location[0] + 1)
                    )
                    for word in matched_words:
                        suggestion_panel.listview.append(ListItem(Static(word)))
