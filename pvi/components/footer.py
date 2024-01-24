from textual.widgets import Input, Static
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from rich.style import Style
from textual import events

from utils import read_ini_file, get_pvi_root


class CommandInput(Input, can_focus=True):
    def focus_on_main_editor(self) -> None:
        self.value = "-- NORMAL --"
        self.blur()
        self.app.query_one("MainEditor").focus()

    def on_focus(self, event: events.Focus) -> None:
        self.value = ":"

    def save_file_content(self) -> None:
        try:
            text_area = self.app.query_one("#pvi-text-area")
            store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")

            with open(store["editing_path"], "w") as file:
                file.write(text_area.text)
        except NoMatches:
            pass

    # reset all main editor attributes, typed_key, copied_text, ..
    def reinit_main_editor_attribute(self) -> None:
        main_editor = self.app.query_one("MainEditor")
        main_editor.selection_start = None 
        main_editor.copied_text = ""
        main_editor.typed_key = ""

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.focus_on_main_editor()
        elif event.key == "enter": # execute command
            if self.value == ":q" or self.value == ":exit":
                self.app.exit()

            elif self.value == ":w" or self.value == ":write":
                self.save_file_content() 
                self.reinit_main_editor_attribute()
                self.focus_on_main_editor()

            elif self.value == ":wq":
                self.save_file_content()
                self.app.exit()


class Footer(Container, can_focus= True):
    with open(f"{get_pvi_root()}/pvi/styles/footer_style.tcss", "r") as file:
        DEFAULT_CSS = file.read()

    def compose(self) -> ComposeResult:
        yield CommandInput("-- NORMAL --", id="command-input")
        yield Static("total: 1", id="total-line")
        yield Static("current: 1", id="current-line")

    def update_input(self, value: str) -> None:
        self.query_one("#command-input").value = value

    def update_total_line(self, total_line: int) -> None:
        self.query_one("#total-line").update(renderable=f"total: {str(total_line)}")

    def update_current_line(self, current_line: int) -> None:
        self.query_one("#current-line").update(renderable=f"current: {str(current_line)}")
