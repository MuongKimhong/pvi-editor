from textual.widgets import TextArea, Static
from textual.app import App, ComposeResult
from textual import events, log

from editor import Editor

import argparse
import os


class Main(App):
    def __init__(self, cli_argument):
        self.cli_argument = cli_argument
        super().__init__()

    def on_mount(self):
        log("Hello world")
        if self.cli_argument["path"] == ".":
            working_directory = os.getcwd()
            log(working_directory)
        elif os.path.exists(self.cli_argument["path"]) is False:
            raise Exception( f'''
            Provided path ({self.cli_argument['path']}) is not exists!
            Please provide a valid path
            ''')
        elif os.path.isfile(self.cli_argument["path"]):
            editing_type = "file"
        elif os.path.isdir(self.cli_argument["path"]):
            editing_type = "dir"

        working_directory = self.cli_argument["path"]

        self.install_screen(Editor, "editor")
        self.push_screen("editor")


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("-p", "--path", help="Path to working directory", required=True)
    arguments = vars(arg.parse_args())

    app = Main(cli_argument=arguments)
    app.run()
