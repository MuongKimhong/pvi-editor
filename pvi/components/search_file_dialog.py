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
    def __init__(self, sidebar_contents: list, directory_content_texts: list, sidebar) -> None:
        self.sidebar_contents = sidebar_contents
        self.directory_content_texts = directory_content_texts
        self.sidebar = sidebar
        self.search_result_paths = []
        self.selected_path = ""
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Search files", id="search-file-input"),
            id="search-dialog"
        )

    def load_file_content(self) -> None:
        store = read_ini_file(file_name="stores.ini", section_name="WorkingDirectory") 
        project_root = store["project_root"]
        path_without_root = self.selected_path[len(project_root):].split("/")[1:]

        '''
        current_path define <project_root + path> in loop  
        or <current_path + path> in loop 
        '''
        current_path = ""

        log(path_without_root)
        log(self.sidebar)
        log(self.directory_content_texts)

        for path in path_without_root:
            log("run 1")
            if current_path == "":
                current_path = project_root + path
            else:
                current_path = current_path + path

            for content in self.directory_content_texts:
                log("run2")
                log(content.content_path)
                log(current_path)
                if content.content_path == current_path:
                    if self.sidebar.content_states.get(f"content_{content.content_id}") is None:
                        self.sidebar.content_states[f"content_{content.content_id}"] = "close"

                    if self.sidebar.content_states[f"content_{content.content_id}"] == "close":
                        self.sidebar.open_directory(selected_dir=content, remount_listview=False) 
                        break

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
                self.search_result_paths.append(content)
            
        if len(self.search_result_paths) > 0:
            if len(self.search_result_paths) > 3:
                search_dialog.styles.height = search_dialog.styles.height.value + len(self.search_result_paths)

            container = SearchResultContainer(listview=ListView(*[])) 
            search_dialog.mount(container)
            container.scroll_visible()

            for result in self.search_result_paths:
                list_item = ListItem(Static(result))
                # list_item.styles.background = "#2E2929"
                self.query_one(SearchResultContainer).listview.append(list_item)

    def on_key(self, event: events.Key) -> None:
        try:
            result_container = self.query_one(SearchResultContainer)
            
            if len(self.search_result_paths) > 1:
                if event.key == "down":
                    result_container.listview.action_cursor_down()
                elif event.key == "up":
                    result_container.listview.action_cursor_up()
                elif event.key == "enter":
                    result_container.listview.action_select_cursor()
        except NoMatches:
            pass
