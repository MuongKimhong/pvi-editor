###########################################################
#                                                         #
# Dialog display when users use <ss> key binding in       #
# Normal mode to search for file in project               #
#                                                         #
###########################################################

from textual.widgets import Input, ListView, ListItem, Static
from textual.screen import ModalScreen
from textual.containers import Container
from textual.css.query import NoMatches
from textual.app import ComposeResult
from textual.containers import Grid
from textual import events, log
import shutil
import os

from utils import read_ini_file


class SearchResultContainer(Container, can_focus=True):
    DEFAULT_CSS = """
        SearchResultContainer {     
            width: 100%;
            content-align: left middle;
            color: white;
            column-span: 2;
            margin-top: 1;
        }
    """

    def __init__(self, listview: ListView) -> None:
        self.listview = listview
        super().__init__()

    def compose(self) -> ComposeResult:
        yield self.listview


class SearchFileDialog(ModalScreen):
    def __init__(self, sidebar_contents: list, directory_content_texts: list, sidebar, sidebar_utils) -> None:
        self.sidebar_contents = sidebar_contents
        self.directory_content_texts = directory_content_texts
        self.sidebar_utils = sidebar_utils
        self.sidebar = sidebar
        self.search_result_paths = []
        self.selected_path = ""

        self.project_root = read_ini_file("stores.ini", "WorkingDirectory")["project_root"]
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Search files", id="search-file-input"),
            id="search-dialog"
        )

    def load_file_content(self) -> None:
        path_split = self.selected_path.split("/")[:-1]
        current_path = self.project_root

        for path in path_split:
            current_path = current_path + "/" + path

            for (index, content) in enumerate(self.sidebar.dir_tree):
                if content["path"] == current_path:
                    contents_above_current_path = self.sidebar.dir_tree[:index + 1]
                    contents_below_current_path = self.sidebar.dir_tree[index + 1:]

                    current_path_contents = os.listdir(current_path)

                    if len(current_path_contents) > 0:
                        files_in_current_path = []
                        directories_in_current_path = []

                        for current_path_content in current_path_contents:
                            c_layer = content["layer_level"] + 1
                            c_path = content["path"] + "/" + current_path_content

                            if os.path.isfile(c_path):
                                files_in_current_path.append(
                                    self.sidebar_utils.content_as_dict(
                                        "file", current_path_content, c_layer, c_path
                                    )
                                )
                            elif os.path.isdir(c_path) and current_path_content != ".git":
                                directories_in_current_path.append(
                                    self.sidebar_utils.content_as_dict(
                                        "dir", current_path_content + "/", c_layer, c_path
                                    )
                                )
                            
                            current_path_contents = [
                                *sorted(directories_in_current_path, key=lambda x: x["content"]),
                                *sorted(files_in_current_path, key=lambda x: x["content"])
                            ]
                            self.sidebar.dir_tree = [
                                *contents_above_current_path,
                                *current_path_contents,
                                *contents_below_current_path
                            ]
                            self.sidebar.content_states[f"content_{index + 1}"] = "open"

        self.dismiss(self.selected_path)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.selected_path = str(event.item._nodes[0].renderable)
        self.load_file_content()

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            self.query_one(SearchResultContainer).remove()
        except NoMatches:
            pass

        search_dialog = self.query_one("#search-dialog")
        search_dialog.styles.height = 10

        self.search_result_paths = []

        for content in self.sidebar_contents:
            if ((event.value in content.split("/")[-1]) and 
                (event.value != "") and 
                (content.split("/")[-1].startswith(event.value))):           

                # remove project_root from content before append
                self.search_result_paths.append(
                    content[len(self.project_root) + 1:]
                )
            
        if len(self.search_result_paths) > 0:
            if len(self.search_result_paths) > 3:
                search_dialog.styles.height = search_dialog.styles.height.value + len(self.search_result_paths)

            container = SearchResultContainer(listview=ListView(*[])) 
            search_dialog.mount(container)
            container.scroll_visible()

            for result in self.search_result_paths:
                list_item = ListItem(Static(result))
                self.query_one(SearchResultContainer).listview.append(list_item)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape": self.dismiss()

        try:
            result_container = self.query_one(SearchResultContainer)
            search_result_len = len(self.search_result_paths)            

            if event.key == "down":
                result_container.listview.action_cursor_down()
            elif event.key == "up":
                result_container.listview.action_cursor_up()
            elif event.key == "enter":
                event.prevent_default()
                result_container.listview.action_select_cursor()
        except NoMatches:
            pass
