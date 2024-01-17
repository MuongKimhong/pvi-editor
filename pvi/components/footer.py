from textual.app import ComposeResult
from textual.widgets import Input
from textual import events

from utils import read_ini_file


class Footer(Input, can_focus=True):
    def set_style(self) -> None:
        style = read_ini_file(file_name="settings.ini", section_name="Footer")
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
        self.value = "--normal--"
        self.blur()
        self.app.query_one("MainEditor").focus()

    def save_file_content(self) -> None:
        store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory")

        if store["argument_parser_type"] == "dir":
            selected_content_index = self.app.query_one("Sidebar").viewing_id - 1
            selected_content = self.app.query("DirectoryContentText")[selected_content_index]

            if selected_content.content_type == "file":
                with open(selected_content.content_path, "w") as file:
                    file.write(self.app.query_one("#pvi-text-area").text)
        else:
            with open(store["editing_path"], "w") as file:
                file.write(self.app.query_one("#pvi-text-area").text)

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
