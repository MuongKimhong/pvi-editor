from textual.widgets.text_area import Selection
from textual.widgets import ListItem
import time
import os

from components.directory_content_text import DirectoryContentText
from components.search_file_dialog import SearchFileDialog
from utils import read_ini_file, SidebarUtils, check_git_diff


class KeyBindingInSelectionMode:
    def __init__(self, main_editor: "MainEditor"):
        self.main_editor = main_editor

    def cancel_selection(self, text_area, old_cursor_location=None) -> None:
        self.main_editor.selection_start = None
        self.main_editor.editing_mode = "normal"
        self.main_editor.app.query_one("Footer").update_input(value="-- NORMAL --")

        if old_cursor_location is not None:
            text_area.selection = Selection(
                start=old_cursor_location, 
                end=old_cursor_location
            )
        else:
            text_area.selection = Selection(
                start=text_area.cursor_location, 
                end=text_area.cursor_location
            )

    def handle_key_binding(self, key_event) -> None:
        text_area = self.main_editor.query_one("#pvi-text-area")  
        footer = self.main_editor.query_one("Footer")

        match key_event.key:
            case "j":
                text_area.action_cursor_down()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
                footer.update_current_line(text_area.cursor_location[0] + 1)
            case "k":
                text_area.action_cursor_up()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )                
                footer.update_current_line(text_area.cursor_location[0] + 1)
            case "l":
                text_area.action_cursor_right()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                ) 
            case "h":
                text_area.action_cursor_left()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                ) 
            case "w":
                text_area.action_cursor_word_right()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "b":
                text_area.action_cursor_word_left()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "A": #upper a
                text_area.action_cursor_line_end()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "I": # upper i
                text_area.action_cursor_line_start()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "y": # copy the selected text
                self.main_editor.copied_text = text_area.selected_text
                self.cancel_selection(text_area)

            case "d": # delete selected text
                if text_area.selected_text != "":
                    old_cursor_location = text_area.cursor_location
                    text_area.delete(
                        start=self.main_editor.selection_start, end=text_area.cursor_location
                    )
                    self.cancel_selection(text_area, old_cursor_location)
           
            case "escape":
                self.cancel_selection(text_area)


class KeyBindingInNormalMode:
    def __init__(self, main_editor: "MainEditor"):
        self.main_editor = main_editor
        self.store = read_ini_file("stores.ini", "WorkingDirectory")

    def enter_insert_mode(self, text_area) -> None:
        self.main_editor.editing_mode = "insert"
        self.main_editor.app.query_one("Footer").update_input("-- INSERT --")
        text_area.focus()

    def enter_selection_mode(self, text_area) -> None:
        self.main_editor.editing_mode = "selection"
        self.main_editor.app.query_one("Footer").update_input("-- SELECTION --")
        self.main_editor.selection_start = text_area.cursor_location
        text_area.selection = Selection(start=text_area.cursor_location, end=text_area.cursor_location)

    def create_new_line(self, text_area) -> None:
        text_area.action_cursor_line_end()
        start, end = text_area.selection
        text_area.replace("\n", start, end, maintain_selection_offset=False)

    def handle_key_binding(self, key_event) -> None:
        text_area = self.main_editor.query_one("#pvi-text-area")
        footer = self.main_editor.query_one("Footer")

        match key_event.key:
            case "j":
                text_area.action_cursor_down()
                footer.update_current_line(text_area.cursor_location[0] + 1)
            case "J":
                line_end = text_area.get_cursor_line_end_location()
                line_text = text_area.document.get_line(text_area.cursor_location[0] + 1).lstrip()

                text_area.move_cursor(line_end)
                text_area.replace(
                    insert=" " + line_text,
                    start=line_end,
                    end=(line_end[0], line_end[1] + len(line_text))
                )
                text_area.move_cursor((text_area.cursor_location[0] + 1, text_area.cursor_location[1]))
                text_area.action_delete_line()
                text_area.move_cursor(line_end)
            case "k":
                text_area.action_cursor_up()
                footer.update_current_line(text_area.cursor_location[0] + 1)
            case "l":
                text_area.action_cursor_right()
            case "h":
                text_area.action_cursor_left()
            case "i":
                self.enter_insert_mode(text_area)
            case "v":
                self.enter_selection_mode(text_area)
            case "o": 
                self.create_new_line(text_area)
                self.enter_insert_mode(text_area)
            case "b":
                text_area.action_cursor_word_left()
            case "w":
                text_area.action_cursor_word_right()
            case "a":
                text_area.move_cursor(
                    (text_area.cursor_location[0], text_area.cursor_location[1] + 1)
                )
                self.enter_insert_mode(text_area)

            case "A": # upper a Case
                text_area.action_cursor_line_end()
                self.enter_insert_mode(text_area)

            case "I": # upper i
                text_area.action_cursor_line_start()
                self.enter_insert_mode(text_area)
            case "escape":
                self.main_editor.typed_key = ""
            case "p": # paste
                if self.main_editor.copied_text != "":
                    self.create_new_line(text_area)
                    text_area.action_cursor_line_end()
                    start, end = text_area.selection
                    text_area.replace(self.main_editor.copied_text, start, end, maintain_selection_offset=False)

            case "left_curly_bracket": # move up 5 cell
                if text_area.cursor_location[0] > 5: # row > 0
                    new_location = (
                        text_area.cursor_location[0] - 5, 
                        text_area.cursor_location[1]
                    )
                    text_area.move_cursor(new_location)
            case "right_curly_bracket": # move down 5 cell
                if text_area.cursor_location[0] < text_area.document.line_count - 1 - 5: # row < last_line - 5
                    new_location = (
                        text_area.cursor_location[0] + 5, 
                        text_area.cursor_location[1]
                    )
                    text_area.move_cursor(new_location)
            case "u": # undo
                if len(text_area.undo_states) > 1:
                    del text_area.undo_states[0]

                    text_area.load_text(text=text_area.undo_states[0]["text"])
                    text_area.move_cursor(text_area.undo_states[0]["cursor"])
        
        ##### key <d> or <dd>
        if key_event.key == "d" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = "d"
            self.main_editor.typed_key_timer = time.time()

        elif key_event.key == "d" and self.main_editor.typed_key == "d": # combination of dd, copy and delete a line
            # if time gaps between first key pressed and second key pressed 
            # greater than 3 seconds, cancel action
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                text_area.action_select_line()
                self.main_editor.copied_text = text_area.selected_text
                text_area.action_delete_line()
                self.main_editor.typed_key = ""

        #### key <sa> and <sl> and <ss>
        elif key_event.key == "s" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = "s"
            self.main_editor.typed_key_timer = time.time()
        
        elif key_event.key == "a" and self.main_editor.typed_key == "s": # <sa> select all
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                self.main_editor.editing_mode = "selection"
                self.main_editor.app.query_one("#footer").update_input(value="-- SELECTION --")
                self.main_editor.selection_start = (0, 0)
                text_area.move_cursor((0, 0)) # move to first line 
                text_area.action_select_all()

        elif key_event.key == "l" and self.main_editor.typed_key == "s": # <sl> select entire line
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                self.main_editor.editing_mode = "selection"
                self.main_editor.app.query_one("#footer").update_input(value="-- SELECTION --")

                text_area.action_cursor_line_start()
                self.main_editor.selection_start = text_area.cursor_location
                text_area.action_cursor_line_end()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )

        # <ss> open search file dialog 
        elif ((key_event.key == "s") and 
              (self.main_editor.typed_key == "s") and 
              (self.store["argument_parser_type"] == "dir")):
              
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                sidebar = self.main_editor.app.query_one("Sidebar")
                sidebar_utils = SidebarUtils(sidebar=sidebar)
                content_paths = self.main_editor.search_project_root()

                # function will be invoked after come back from SearchFileDialog Screen
                def after_select_file(file_path: str, main_editor=self.main_editor, store=self.store, sidebar=sidebar):
                    sidebar_utils.handle_re_mount_listview()

                    for content in main_editor.app.query("DirectoryContentText"):
                        if content.content_path == store["project_root"] + "/" + file_path:
                            sidebar.set_sidebar_width(content.layer_level)
                            sidebar.select_file(content)
                            sidebar.viewing_id = content.content_id 
                            sidebar_utils.set_to_highlighted_or_normal()
                    check_git_diff(main_editor.app)
                
                self.main_editor.app.push_screen(
                    SearchFileDialog(
                        sidebar_contents=content_paths, 
                        directory_content_texts=list(sidebar.query("DirectoryContentText")),
                        sidebar_utils=sidebar_utils,
                        sidebar=sidebar
                    ),
                    after_select_file
                )
            
        #### key <yy>
        elif key_event.key == "y" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = "y"
            self.main_editor.typed_key_timer = time.time()

        elif key_event.key == "y" and self.main_editor.typed_key == "y": # yy, copy the entire line
            if time.time() - self.main_editor.typed_key_timer > 3:
                    self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                old_cursor_location = text_area.cursor_location
                text_area.action_cursor_line_start()
                text_area.action_select_line()
                self.main_editor.copied_text = text_area.selected_text
                text_area.selection = Selection(start=old_cursor_location, end=old_cursor_location)

        #### key <gt> or <gb> 
        elif key_event.key == "g" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = "g"
            self.main_editor.typed_key_timer = time.time()

        elif key_event.key == "t" and self.main_editor.typed_key == "g": # <gt> go top
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                text_area.move_cursor((0, 0))

        elif key_event.key == "b" and self.main_editor.typed_key == "g": # <gb> go bottom
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                # starting index is 0 for Tuple[row, column]
                last_line = text_area.document.line_count - 1
                text_area.move_cursor((last_line, 0))