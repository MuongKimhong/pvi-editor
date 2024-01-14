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

        result_paths = []

        for content in self.sidebar_contents:
            if ((event.value in content.split("/")[-1]) and 
                (event.value != "") and 
                (content.split("/")[-1].startswith(event.value))):           
                result_paths.append(content)
            
        if len(result_paths) > 0:
            if len(result_paths) > 3:
                search_dialog.styles.height = search_dialog.styles.height.value + len(result_paths)

            container = SearchResultContainer(listview=ListView(*[])) 
            search_dialog.mount(container)
            container.scroll_visible()

            for result in result_paths:
                list_item = ListItem(Static(result))
                self.query_one(SearchResultContainer).listview.append(list_item)
