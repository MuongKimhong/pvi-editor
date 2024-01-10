from textual.widgets import TextArea, Static
from textual import events, log

from autocomplete import AutoComplete
import time


class PviTextArea(TextArea):
    autocomplete_symbol = ['{', '[', '(']
    autocomplete_engine = AutoComplete()

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

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normal--") 

        elif event.character in self.autocomplete_symbol:
            self.handle_autocomplete_symbol(character=event.character)

        elif event.key == "s":
            start = time.time()
            all_suggestions = self.autocomplete_engine.python_autocomplete(self.document.text)        
            # log(all_suggestions)
            log(time.time() - start)
         
        # elif event.key == "s":
            # static = Static("Good evening", id="text")
            # # static.styles.layer = "above"
            # # static.styles.width = 50
            # # static.styles.height = 10
            # # static.styles.content_align = ("center", "middle")
            # # static.styles.offset = (13, 6)
            # # static.styles.background = "yellow"
            # # static.styles.color = "white"
            # self.mount(static)
            # static.scroll_visible()