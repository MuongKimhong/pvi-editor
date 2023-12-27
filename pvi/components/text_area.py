from textual.widgets import TextArea
from textual import events


class PviTextArea(TextArea):
    def set_selection_start(self, start_location) -> None:
        self.selection.start = start_location

    def set_selection_end(self, end_location) -> None:
        self.selection.end = end_location

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.blur()
            self.app.query_one("#footer").change_value(value="--normall--") 
