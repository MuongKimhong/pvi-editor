from textual.widgets import TextArea, Static
from textual.app import App, ComposeResult
from textual import events, log


from components.sidebar import Sidebar


class Main(App):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Sidebar()
        yield Static("Two", id="editor")

    def toggle_sidebar(self) -> None:
        width = self.query_one(Sidebar).styles.width.value

        self.query_one(Sidebar).styles.width = 0 if width == 30 else 30
        self.query_one(Sidebar).styles.border = ("hidden", "grey") if width == 30 else ("round", "grey")

    def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+b":
            self.toggle_sidebar()        


if __name__ == "__main__":
    app = Main()
    app.run()
