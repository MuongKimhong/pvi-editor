from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Container
from textual import events, log

from utils import read_setting_ini_file, read_store_ini_file


class Footer(Input, can_focus=True):
    def set_style(self) -> None:
        style = read_setting_ini_file(section_name="Footer")
        self.styles.dock = "bottom" #  can't be changed
        self.styles.width = "100%" # can't be changed
        self.styles.height = int(style["height"])
        self.styles.background = f"#{style['background_color']}"
        self.styles.color = style["text_color"]
        self.styles.border = ("hidden", "grey")
        
    def on_mount(self, event: events.Mount) -> None:
        self.value = "--normal--"
        self.set_style()

    def on_focus(self, event: events.Focus) -> None:
        self.value = ":"

    def change_value(self, value: str) -> None:
        self.value = value

    def focus_on_main_editor(self) -> None:
        self.value = "--normall--"
        self.blur()
        self.app.query_one("MainEditor").focus()

    def save_file_content(self) -> None:
        store = read_store_ini_file(section_name="WorkingDirectory")
        selected_content_index = self.app.query_one("Sidebar").viewing["id"] - 1
        selected_content = self.app.query("DirectoryContentText")[selected_content_index]

        if selected_content.content_type == "file":
            with open(f"{store['editing_path']}/{selected_content.content_name}", "w") as file:
                file.write(self.app.query_one("#pvi-text-area").text)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.focus_on_main_editor()
        elif event.key == "enter": # execute command
            if self.value == ":q" or self.value == ":exit":
                self.app.exit()

            elif self.value == ":w" or self.value == ":write":
                self.save_file_content() 
                self.focus_on_main_editor()
