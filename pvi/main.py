from textual.widgets import TextArea, Static
from textual.app import App, ComposeResult
from textual import events, log

from editor import Editor


class Main(App):
    def on_mount(self):
        self.install_screen(Editor, "editor")
        self.push_screen("editor")


if __name__ == "__main__":
    app = Main()
    app.run()
