#!/usr/bin/env python3

'''
Entry Point for development mode
'''
from textual.widgets import TextArea, Static
from textual.app import App, ComposeResult
from textual import events

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
        argument = self.cli_argument["argument"]
        argument_split = self.cli_argument["argument"].split("/")[1:]

        if argument == ".":
            section_data["editing_path"] = os.getcwd()
            section_data["project_root"] = os.getcwd()
            section_data["editing_type"] = "dir"
            section_data["argument_parser_type"] = "dir"
        elif os.path.isdir(argument):
            section_data["editing_path"] = os.getcwd() + "/" + argument
            section_data["project_root"] = os.getcwd() + "/" + argument
            section_data["editing_type"] = "dir"
            section_data["argument_parser_type"] = "dir"
        elif os.path.isfile(argument):
            section_data["editing_path"] = os.getcwd() + "/" + argument
            section_data["project_root"] = os.getcwd()
            section_data["editing_type"] = "file"
            section_data["argument_parser_type"] = "file"

        update_ini_file(file_name="stores.ini", section_name="WorkingDirectory", section_data=section_data)
        self.install_screen(Editor, "editor")
        self.push_screen("editor")


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("argument", nargs="?", help="a file or directory or current directory") 
    arguments = vars(arg.parse_args())
    app = Main(cli_argument=arguments)
    app.run()