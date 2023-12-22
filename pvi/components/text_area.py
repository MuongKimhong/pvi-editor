from textual.widgets import TextArea
from textual import events


class PviTextArea(TextArea):
    def on_key(self, event: events.Key) -> None:
        pass