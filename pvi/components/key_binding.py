from textual.widgets.text_area import Selection
from textual import log
import numpy
import time


class KeyBindingInSelectionMode:
    def __init__(self, main_editor):
        self.main_editor = main_editor

    def cancel_selection(self, text_area, old_cursor_location=None) -> None:
        self.main_editor.selection_start = None
        self.main_editor.editing_mode = "normal"
        self.main_editor.app.query_one("#footer").change_value(value="--normal--")

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

        match key_event.key:
            case "j":
                text_area.action_cursor_down()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )
            case "k":
                text_area.action_cursor_up()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
                )                
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
                    log("d in selection pressed")
                    old_cursor_location = text_area.cursor_location
                    text_area.delete(
                        start=self.main_editor.selection_start, end=text_area.cursor_location
                    )
                    self.cancel_selection(text_area, old_cursor_location)
           
            case "escape":
                self.cancel_selection(text_area)


class KeyBindingInNormalMode:
    def __init__(self, main_editor):
        self.main_editor = main_editor

    def enter_insert_mode(self, text_area) -> None:
        self.main_editor.editing_mode = "insert"
        self.main_editor.app.query_one("#footer").change_value(value="--insert--")
        text_area.focus()

    def enter_selection_mode(self, text_area) -> None:
        self.main_editor.editing_mode = "selection"
        self.main_editor.app.query_one("#footer").change_value(value="--selection--")
        self.main_editor.selection_start = text_area.cursor_location
        text_area.selection = Selection(start=text_area.cursor_location, end=text_area.cursor_location)

    def create_new_line(self, text_area) -> None:
        text_area.action_cursor_line_end()
        start, end = text_area.selection
        text_area.replace("\n", start, end, maintain_selection_offset=False)

    def handle_key_binding(self, key_event) -> None:
        text_area = self.main_editor.query_one("#pvi-text-area")

        match key_event.key:
            case "j":
                text_area.action_cursor_down()
            case "k":
                text_area.action_cursor_up()
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

            case "A": # upper a
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

        #### key <sa> and <sl>
        elif key_event.key == "s" and self.main_editor.typed_key == "":
            self.main_editor.typed_key = "s"
            self.main_editor.typed_key_timer = time.time()
        
        elif key_event.key == "a" and self.main_editor.typed_key == "s": # <sa> select all
            if time.time() - self.main_editor.typed_key_timer > 3:
                self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                self.main_editor.editing_mode = "selection"
                self.main_editor.app.query_one("#footer").change_value(value="--selection--")
                self.main_editor.selection_start = (0, 0)
                text_area.move_cursor((0, 0)) # move to first line 
                text_area.action_select_all()

        elif key_event.key == "l" and self.main_editor.typed_key == "s": # <sl> select entire line
            if time.time() - self.main_editor.typed_key_timer > 3:
                    self.main_editor.reset_typed_key()
            else:
                self.main_editor.typed_key = ""
                self.main_editor.editing_mode = "selection"
                self.main_editor.app.query_one("#footer").change_value(value="--selection--")

                text_area.action_cursor_line_start()
                self.main_editor.selection_start = text_area.cursor_location
                text_area.action_cursor_line_end()
                text_area.selection = Selection(
                    start=self.main_editor.selection_start, end=text_area.cursor_location
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