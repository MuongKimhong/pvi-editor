from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static


class DirectoryContentText(Container):
    def __init__(self, content_name: str, content_type: str, content_id: int, layer_level: int) -> None:
        self.content_name: str = content_name
        self.content_type: str = content_type
        self.content_id: int = content_id
        self.layer_level: int = layer_level + 1 if layer_level > 0 else 0
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(self.content_name)

    def set_to_highlighted(self) -> None:
        self.styles.background = "grey"
        self.styles.text_style = "bold"
        self.styles.color = "cyan" if self.content_type == "dir" else "white"

    def set_to_normal(self) -> None:
        self.styles.background = "#242424"
        if self.content_type == "dir":
            self.styles.color = "cyan"
            self.styles.text_style = "bold"
        else:
            self.styles.color = "white"

    def on_mount(self, event: events.Mount) -> None:
        self.set_to_normal()
        self.query_one(Static).styles.padding = (0, 0, 0, self.layer_level)
