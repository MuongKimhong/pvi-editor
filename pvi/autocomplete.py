import subprocess
import os

import re


class AutoComplete:
    def __init__(self, language):
        self.language = language
    
    def filter_pattern(self, patterns: list) -> list:
        filtered_pattern = []

        for pattern in patterns:
            if (pattern != "") and (pattern not in filtered_pattern):
                filtered_pattern.append(pattern)

        return filtered_pattern

    def get_suggestion(self, code) -> list:
        if self.language == "python":
            return self.python_autocomplete(code)
    
    def python_autocomplete(self, code):
        patterns = re.compile(r'\b(?:def|class|from|import|([a-zA-Z_]\w*)\s*\(.*?\))')
        return self.filter_pattern(patterns=patterns.findall(code))

    def javascript_autocomplete(self):
        pass
