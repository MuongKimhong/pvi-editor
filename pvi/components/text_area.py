from textual.widgets import TextArea
from textual import events


class PviTextArea(TextArea):
    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normal--") 
