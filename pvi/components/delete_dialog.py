###########################################################
#                                                         #
# Dialog display when users use <dd> key binding in       #
# sidebar to delete file or directory                     #
#                                                         #
###########################################################

from textual.widgets import Button, Static, Label
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid
from textual import events
import shutil
import os


class DeleteDialog(ModalScreen):
    def __init__(self, content_to_delete: "DirectoryContentText") -> None:
        self.content_to_delete = content_to_delete
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to delete?", id="question"),
            Button("Delete", variant="error", id="delete"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog"
        )

    def delete_action(self) -> None:
        c_type = self.content_to_delete.content_type
        c_path = self.content_to_delete.content_path

        if c_type == "file":
            os.remove(c_path)     
        elif (c_type == "dir") and (len(os.listdir(c_path)) == 0): # empty dir
            os.rmdir(c_path)
        elif (c_type == "dir") and (len(os.listdir(c_path)) > 0):
            shutil.rmtree(c_path)

        # invoke function after_delete_action in editor screen
        # -> self.app.push_screen(DeleteDialog(content_to_delete=content_to_delete), after_delete_action)
        self.dismiss(self.content_to_delete)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            self.delete_action()
        else:
            self.dismiss()
