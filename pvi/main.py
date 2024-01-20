#!/usr/bin/env python3
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
        # # pvi -d some_directory
        # if self.cli_argument["directory"]:
        #     if os.path.exists(self.cli_argument["directory"]) and os.path.isdir(self.cli_argument["directory"]):
        #         section_data["editing_path"] = f"{os.getcwd()}/{self.cli_argument['directory']}"
        #         section_data["project_root"] = f"{os.getcwd()}/{self.cli_argument['directory']}"
        #         section_data["editing_type"] = "dir"
        #         section_data["argument_parser_type"] = "dir"
        #     else:
        #         raise Exception(f'''
        #         \n[Error] No directory found. "{self.cli_argument['file_or_current_directory']}".\n 
        #         ''')
        
        # elif self.cli_argument["file_or_current_directory"]:
        #     # pvi .  : open current directory
        #     if self.cli_argument["file_or_current_directory"] == ".":
        #         section_data["editing_path"] = os.getcwd()
        #         section_data["project_root"] = os.getcwd()
        #         section_data["editing_type"] = "dir"
        #         section_data["argument_parser_type"] = "dir"

        #     else: 
        #         # pvi somefile.py : open somefile.py
        #         if os.path.exists(self.cli_argument["file_or_current_directory"]):
        #             if os.path.isfile(self.cli_argument["file_or_current_directory"]):
        #                 section_data["editing_path"] = f"{os.getcwd()}/{self.cli_argument['file_or_current_directory']}"
        #                 section_data["project_root"] = os.getcwd()
        #                 section_data["editing_type"] = "file"
        #                 section_data["argument_parser_type"] = "file"
        #         else:
        #             raise Exception(f'''
        #             \n[Error] No such file "{self.cli_argument['file_or_current_directory']}".\n 
        #             ''')
        
        # else:
        #     raise Exception('''
        #     \n[Error] The provided argument is not supported! Please check the documentation for more detail.\n
        #     ''')
        # update_ini_file(file_name="stores.ini", section_name="WorkingDirectory", section_data=section_data)

        # self.install_screen(Editor, "editor")
        # self.push_screen("editor")
        argument = self.cli_argument["argument"]
        argument_split = self.cli_argument["argument"].split("/")[1:]

        if argument_split[-1] == ".":
            section_data["editing_path"] = argument[:-2] # remove /. from arguemnt
            section_data["project_root"] = argument[:-2]
            section_data["editing_type"] = "dir"
            section_data["argument_parser_type"] = "dir"
        elif os.path.isdir(argument):
            # remove / from the end of argument if any
            section_data["editing_path"] = argument[:-1] if argument[-1] == "/" else argument
            section_data["project_root"] = argument[:-1] if argument[-1] == "/" else argument
            section_data["editing_type"] = "dir"
            section_data["argument_parser_type"] = "dir"
        elif os.path.isfile(argument):
            section_data["editing_path"] = argument
            section_data["project_root"] = "/" + "/".join(argument_split[:-1])
            section_data["editing_type"] = "file"
            section_data["argument_parser_type"] = "file"

        update_ini_file(file_name="stores.ini", section_name="WorkingDirectory", section_data=section_data)

        self.install_screen(Editor, "editor")
        self.push_screen("editor")


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    # arg.add_argument("-d", "--directory", help="Open a directory", required=False)
    # arg.add_argument("file_or_current_directory", nargs="?", help="a file to edit or a current directory to open")

    arg.add_argument("argument", nargs="?", help="a file or directory or current directory")
    arguments = vars(arg.parse_args())

    app = Main(cli_argument=arguments)
    app.run()
