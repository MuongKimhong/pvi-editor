from textual.widgets.text_area import TextAreaTheme
from tree_sitter_languages import get_language
from rich.style import Style
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


    def my_theme(self) -> TextAreaTheme:
        return TextAreaTheme(
            name="my_theme",
            base_style=Style(color="#f8f8f2", bgcolor="#181717"),
            gutter_style=Style(color="#6272a4"),
            cursor_style=Style(color="#282a36", bgcolor="#f8f8f0"),
            cursor_line_style=Style(bgcolor="#282b45"),
            cursor_line_gutter_style=Style(color="#c2c2bf", bgcolor="#282b45", bold=True),
            bracket_matching_style=Style(bgcolor="#99999d", bold=True, underline=True),
            selection_style=Style(bgcolor="#44475A"),
            syntax_styles={
                "string": Style(color="#f1fa8c"),
                "string.documentation": Style(color="#f1fa8c"),
                "comment": Style(color="#6272a4"),
                "keyword": Style(color="#ff79c6"),
                "operator": Style(color="#ff79c6"),
                "repeat": Style(color="#ff79c6"),
                "exception": Style(color="#ff79c6"),
                "include": Style(color="#ff79c6"),
                "keyword.function": Style(color="#ff79c6"),
                "keyword.return": Style(color="#ff79c6"),
                "keyword.operator": Style(color="#ff79c6"),
                "conditional": Style(color="#ff79c6"),
                "number": Style(color="#bd93f9"),
                "float": Style(color="#bd93f9"),
                "class": Style(color="#50fa7b"),
                "class.call": Style(color="#50fa7b"),
                "type.class": Style(color="#50fa7b"),
                "function": Style(color="#50fa7b"),
                "function.call": Style(color="#50fa7b"),
                "method": Style(color="#50fa7b"),
                "method.call": Style(color="#50fa7b"),
                "boolean": Style(color="#bd93f9"),
                "json.null": Style(color="#bd93f9"),
                "regex.punctuation.bracket": Style(color="#ff79c6"),
                "regex.operator": Style(color="#ff79c6"),
                "html.end_tag_error": Style(color="#F83333", underline=True),
                "tag": Style(color="#ff79c6"),
                "yaml.field": Style(color="#ff79c6", bold=True),
                "json.label": Style(color="#ff79c6", bold=True),
                "toml.type": Style(color="#ff79c6"),
                "toml.datetime": Style(color="#bd93f9"),
                "heading": Style(color="#ff79c6", bold=True),
                "bold": Style(bold=True),
                "italic": Style(italic=True),
                "strikethrough": Style(strike=True),
                "link": Style(color="#bd93f9", underline=True),
                "inline_code": Style(color="#f1fa8c"),
                "punctuation.special": Style(color="#2569d8"),
            },
        )

    def my_theme_insert_mode(self) -> TextAreaTheme:
        return TextAreaTheme(
            name="my_theme_insert_mode",
            base_style=Style(color="#f8f8f2", bgcolor="#181717"),
            gutter_style=Style(color="#6272a4"),
            cursor_style=Style(color="#282a36", bgcolor="#1F95DD"),
            cursor_line_style=Style(bgcolor="#282b45"),
            cursor_line_gutter_style=Style(color="#c2c2bf", bgcolor="#282b45", bold=True),
            bracket_matching_style=Style(bgcolor="#99999d", bold=True, underline=True),
            selection_style=Style(bgcolor="#44475A"),
            syntax_styles={
                "string": Style(color="#f1fa8c"),
                "string.documentation": Style(color="#f1fa8c"),
                "comment": Style(color="#6272a4"),
                "keyword": Style(color="#ff79c6"),
                "operator": Style(color="#ff79c6"),
                "repeat": Style(color="#ff79c6"),
                "exception": Style(color="#ff79c6"),
                "include": Style(color="#ff79c6"),
                "keyword.function": Style(color="#ff79c6"),
                "keyword.return": Style(color="#ff79c6"),
                "keyword.operator": Style(color="#ff79c6"),
                "conditional": Style(color="#ff79c6"),
                "number": Style(color="#bd93f9"),
                "float": Style(color="#bd93f9"),
                "class": Style(color="#50fa7b"),
                "class.call": Style(color="#50fa7b"),
                "type.class": Style(color="#50fa7b"),
                "function": Style(color="#50fa7b"),
                "function.call": Style(color="#50fa7b"),
                "method": Style(color="#50fa7b"),
                "method.call": Style(color="#50fa7b"),
                "boolean": Style(color="#bd93f9"),
                "json.null": Style(color="#bd93f9"),
                "regex.punctuation.bracket": Style(color="#ff79c6"),
                "regex.operator": Style(color="#ff79c6"),
                "html.end_tag_error": Style(color="#F83333", underline=True),
                "tag": Style(color="#ff79c6"),
                "yaml.field": Style(color="#ff79c6", bold=True),
                "json.label": Style(color="#ff79c6", bold=True),
                "toml.type": Style(color="#ff79c6"),
                "toml.datetime": Style(color="#bd93f9"),
                "heading": Style(color="#ff79c6", bold=True),
                "bold": Style(bold=True),
                "italic": Style(italic=True),
                "strikethrough": Style(strike=True),
                "link": Style(color="#bd93f9", underline=True),
                "inline_code": Style(color="#f1fa8c"),
                "punctuation.special": Style(color="#2569d8"),
            },
        )