from tree_sitter_languages import get_language
from pathlib import Path

from utils import get_pvi_root


class Syntax:
    def __init__(self) -> None:
        self.add_on_spp_lg = {
            "c"   : "c",
            "cpp" : "cpp",
            "js"  : "javascript",
            "ts"  : "typescript",
            "java": "java",
            "php" : "php",
            "rb"  : "ruby", 
            "rs"  : "rust"
        }
        self.textual_spp_lg = {
            "sql" : "sql",
            "md"  : "markdown",
            "html": "html",
            "toml": "toml",
            "css" : "css",
            "yml" : "yaml",
            "json": "json",
            "py"  : "python",
        }

    def textual_spp(self, file_name: str) -> bool:
        file_ext = file_name.split(".")[-1] 
        return True if file_ext in self.textual_spp_lg else False

    # match the file type with sp languages
    def file_type_to_tree_sitter_language(self, file_name: str):
        file_ext = file_name.split(".")[-1]

        if file_ext in self.add_on_spp_lg:
            return get_language(self.add_on_spp_lg.get(file_ext))

        if file_ext in self.textual_spp_lg:
            return get_language(self.textual_spp_lg.get(file_ext))

        return None

    def file_type_to_language(self, file_name: str):
        file_ext = file_name.split(".")[-1]

        if file_ext in self.add_on_spp_lg:
            return self.add_on_spp_lg.get(file_ext)

        if file_ext in self.textual_spp_lg:
            return self.textual_spp_lg.get(file_ext)

        return None

    def get_highlight_query(self, language: str):
        return (get_pvi_root() / f"pvi/highlight_query/{language}_highlights.scm").read_text()
