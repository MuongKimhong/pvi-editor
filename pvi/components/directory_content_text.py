from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static
from textual import events
from rich.style import Style


class DirectoryContentText(Container):
    def __init__(self, 
                content_name: str, 
                content_type: str, 
                content_id: int, 
                layer_level: int,
                content_path: str) -> None:

        self.content_name = content_name
        self.content_type = content_type
        self.content_id = content_id
        self.content_path = content_path
        self.layer_level = layer_level + 1 if layer_level > 0 else 0
        self.file_opened = False
        super().__init__()

    def compose(self) -> ComposeResult:
        # yield Static(self.content_name)
        left_a = "\u2764"
        yield Static(f"{left_a} {self.content_name}")

    def set_to_highlighted(self) -> None:
        self.styles.background = "grey"
        self.styles.text_style = Style(bold=True)
        self.styles.color = "cyan" if self.content_type == "dir" else "white"

    def set_to_highlighted_after_selected_file(self) -> None:
        self.styles.background = "#424141"
        self.styles.text_style = Style(bold=True)
        self.styles.color = "white"

    def set_to_normal(self) -> None:
        self.styles.background = "#131212"
        if self.content_type == "dir":
            self.styles.color = "cyan"
            self.styles.text_style = Style(bold=True)
        else:
            self.styles.color = "white"
            self.styles.text_style = Style(bold=False)

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(Static).styles.padding = (0, 0, 0, self.layer_level)
