from textual.widgets import TextArea, Static
from textual.app import App, ComposeResult
from textual import events, log

from utils import update_store_ini_file
from editor import Editor

import argparse
import os


class Main(App):
    def __init__(self, cli_argument):
        self.cli_argument = cli_argument
        super().__init__()

    def on_mount(self):
        section_data = {"directory_path": None, "editing_type": None}

        if self.cli_argument["currentworkingdirectory"] == ".":
            section_data["directory_path"] = os.getcwd()
            section_data["editing_type"] = "dir"

        elif self.cli_argument["directory"]: 
            if os.path.exists(self.cli_argument["directory"]) and os.path.isdir(self.cli_argument["directory"]):
                section_data["directory_path"] = f"{os.getcwd()}/{self.cli_argument['directory']}"
                section_data["editing_type"] = "dir"

        elif self.cli_argument["file"]: 
            if os.path.exists(self.cli_argument["file"]) and os.path.isfile(self.cli_argument["file"]):
                section_data["directory_path"] = f"{os.getcwd()}/{self.cli_argument['file']}"
                section_data["editing_type"] = "file"

        elif self.cli_argument["fullpath"]: 
            if os.path.exists(self.cli_argument["fullpath"]):
                section_data["directory_path"] = self.cli_argument["fullpath"]
                section_data["editing_type"] = "file" if os.path.isfile(self.cli_argument["fullpath"]) else "dir"
        
        else:
            raise Exception('''
            \n[Error] The provided argument is not supported! Please check the documentation for more detail.\n
            ''')

        update_store_ini_file(section_name="WorkingDirectory", section_data=section_data)

        self.install_screen(Editor, "editor")
        self.push_screen("editor")


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("-p", "--fullpath", help="Open a file or directory with provided full path", required=False)
    arg.add_argument("-w", "--currentworkingdirectory", help="Open current working directory", required=False)
    arg.add_argument("-d", "--directory", help="Open a directory", required=False)
    arg.add_argument("-f", "--file", help="Open a file", required=False)
    arguments = vars(arg.parse_args())

    app = Main(cli_argument=arguments)
    app.run()
