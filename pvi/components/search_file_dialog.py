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
    def __init__(self, sidebar_contents: list) -> None:
        self.sidebar_contents = sidebar_contents
        self.search_result_paths = []
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Search files", id="search-file-input"),
            id="search-dialog"
        )

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
                    pass
        except NoMatches:
            pass
