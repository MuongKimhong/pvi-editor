from textual.widgets import TextArea, Static
from textual.app import App, ComposeResult
from textual import events, log

from utils import update_ini_file
from editor import Editor

import argparse
import os


class Main(App):
    def __init__(self, cli_argument):
        self.cli_argument = cli_argument
        super().__init__()

    def on_mount(self):
        section_data = {
            "editing_path": None, 
            "editing_type": None, 
            "project_root": None, 
            "argument_parser_type": None
        }

        # pvi -d some_directory
        if self.cli_argument["directory"]:
            if os.path.exists(self.cli_argument["directory"]) and os.path.isdir(self.cli_argument["directory"]):
                section_data["editing_path"] = f"{os.getcwd()}/{self.cli_argument['directory']}"
                section_data["project_root"] = f"{os.getcwd()}/{self.cli_argument['directory']}"
                section_data["editing_type"] = "dir"
                section_data["argument_parser_type"] = "dir"
        
        elif self.cli_argument["file_or_current_directory"]:
            # pvi .  : open current directory
            if self.cli_argument["file_or_current_directory"] == ".":
                section_data["editing_path"] = os.getcwd()
                section_data["project_root"] = os.getcwd()
                section_data["editing_type"] = "dir"
                section_data["argument_parser_type"] = "dir"
            
            # pvi somefile.py : open somefile.py
            elif os.path.exists(self.cli_argument["file_or_current_directory"]):
                if os.path.isfile(self.cli_argument["file_or_current_directory"]):
                    section_data["editing_path"] = f"{os.getcwd()}/{self.cli_argument['file_or_current_directory']}"
                    section_data["project_root"] = os.getcwd()
                    section_data["editing_type"] = "file"
                    section_data["argument_parser_type"] = "file"
        
        else:
            raise Exception('''
            \n[Error] The provided argument is not supported! Please check the documentation for more detail.\n
            ''')

        update_ini_file(file_name="stores.ini", section_name="WorkingDirectory", section_data=section_data)

        self.install_screen(Editor, "editor")
        self.push_screen("editor")


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("-d", "--directory", help="Open a directory", required=False)
    arg.add_argument("file_or_current_directory", nargs="?", help="a file to edit or a current directory to open")
    arguments = vars(arg.parse_args())

    app = Main(cli_argument=arguments)
    app.run()
