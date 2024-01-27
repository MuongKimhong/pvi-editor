from textual.widgets import Input, Static
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from rich.style import Style
from textual import events, log

from utils import read_ini_file, get_pvi_root, check_git_diff

import subprocess
import re


class CommandInput(Input, can_focus=True):
    err_occur = False
    git_command_pattern = re.compile(r'^:git push origin (\S+) \"(.*?)\"')    
    git_push_all_pattern = re.compile(r'^:push (\S+) \"(.*?)\"')

    def focus_on_main_editor(self) -> None:
        self.styles.color = "white"
        self.err_occur = False
        self.value = "-- NORMAL --"
        self.blur()
        self.app.query_one("MainEditor").focus()

    def on_focus(self, event: events.Focus) -> None:
        self.value = ":"

    def save_file_content(self) -> None:
        try:
            text_area = self.app.query_one("#pvi-text-area")
            store = read_ini_file("stores.ini", "WorkingDirectory")

            with open(store["editing_path"], "w") as file:
                file.write(text_area.text)
            
            check_git_diff(main_app=self.app)
            
        except NoMatches:
            pass

    def show_err_msg(self, msg: str) -> None:
        self.err_occur = True
        self.styles.color = "red"
        self.value = msg

    # reset all main editor attributes, typed_key, copied_text, ..
    def reinit_main_editor_attribute(self) -> None:
        main_editor = self.app.query_one("MainEditor")
        main_editor.selection_start = None 
        main_editor.copied_text = ""
        main_editor.typed_key = ""

    def git_commit_and_push(self, patterns, push_all=True):
        branch = patterns.group(1)
        message = patterns.group(2)
        sh_path = f"{get_pvi_root()}/git_command.sh"
        file_path = read_ini_file("stores.ini", "WorkingDirectory")["editing_path"]
        command = ["bash", sh_path, branch, message] if push_all else ["bash", sh_path, branch, message, file_path]

        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        ) 
        process.wait()

        if process.returncode == 0:
            self.focus_on_main_editor()
        else:
            self.show_err_msg(msg="error git command")

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.focus_on_main_editor()

        if self.err_occur:
            event.prevent_default()
        else:
            if event.key == "enter": # execute command
                # :git push origin branchname "message"
                match_patterns = self.git_command_pattern.match(self.value)
                push_all_match_patterns = self.git_push_all_pattern.match(self.value)

                if self.value == ":q" or self.value == ":exit":
                    self.app.exit()

                elif self.value == ":w" or self.value == ":write":
                    self.save_file_content() 
                    self.reinit_main_editor_attribute()
                    self.focus_on_main_editor()

                elif self.value == ":wq":
                    self.save_file_content()
                    self.app.exit()

                # :push branchname "message", push everthing
                elif push_all_match_patterns:
                    self.git_commit_and_push(patterns=push_all_match_patterns, push_all=True)
                
                # :git push origin branchname "message", push only editing_path
                elif match_patterns:
                    self.git_commit_and_push(patterns=match_patterns, push_all=False)
                else:
                    self.show_err_msg(msg="unknow command")


class Footer(Container, can_focus= True):
    with open(f"{get_pvi_root()}/pvi/styles/footer_style.tcss", "r") as file:
        DEFAULT_CSS = file.read()

    def compose(self) -> ComposeResult:
        yield CommandInput("-- NORMAL --", id="command-input")
        yield Static("total: 0", id="total-line")
        yield Static("current: 0", id="current-line")

    def update_input(self, value: str) -> None:
        self.query_one("#command-input").value = value

    def update_total_line(self, total_line: int) -> None:
        self.query_one("#total-line").update(renderable=f"total: {str(total_line)}")

    def update_current_line(self, current_line: int) -> None:
        self.query_one("#current-line").update(renderable=f"current: {str(current_line)}")
