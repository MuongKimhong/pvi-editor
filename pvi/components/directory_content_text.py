from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static
from textual import events
from rich.style import Style

from icon import Icon


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
        state = self.app.query_one("Sidebar").content_states[f"content_{self.content_id}"]

        if self.content_type == "dir" and state == "open":
            display = f"{Icon.DOWN_ARROW} {Icon.OPENED_FOLDER} {self.content_name}"
        elif self.content_type == "dir" and state == "close":
            display = f"{Icon.RIGHT_ARROW} {Icon.CLOSED_FOLDER} {self.content_name}"
        else:
            display = " " + f" {Icon.FILE} {self.content_name}"

        yield Static(display)

    def set_to_highlighted(self) -> None:
        self.styles.background = "#44475A"
        self.styles.text_style = Style(bold=True)

    def set_to_highlighted_after_selected_file(self) -> None:
        self.styles.background = "#44475A"
        self.styles.text_style = Style(bold=True)

    def set_to_normal(self) -> None:
        self.styles.background = "#131212"
        self.styles.text_style = Style(bold=True) if self.content_type == "dir" else Style(bold=False)

    def set_to_git_changes_detected(self) -> None:
        self.styles.color = "orange"

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(Static).styles.padding = (0, 0, 0, self.layer_level)
