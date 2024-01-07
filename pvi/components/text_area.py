from textual.widgets import TextArea, Static
from textual import events, log


class PviTextArea(TextArea):
    autocomplete_symbol = ['"', '{', '[', '(', '`', "'"]

    DEFAULT_CSS = """
    PviTextArea {
        layers: above;
    } 
    """

    def handle_autocomplete_symbol(self, character) -> None:
        if character == "{":
            text = "}"            
        elif character == "[":
            text = "]"
        elif character == "(":
            text = ")"
        else:
            text = character

        self.document.replace_range(
            start=self.cursor_location,
            end=(self.cursor_location[0], self.cursor_location[1] + 1),
            text=text
        )

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normal--") 

        elif event.character in self.autocomplete_symbol:
            self.handle_autocomplete_symbol(character=event.character)

        elif event.key == "s":
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