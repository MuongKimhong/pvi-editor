import subprocess
import os

import re


class AutoComplete:
    # def __init__(self, language):
    #     self.language = language
    
    def python_autocomplete(self, code):
        pattern = re.compile(r'\b(?:def|class|from|import|([a-zA-Z_]\w*)\s*\(.*?\))')
        filtered_pattern = []

        for pattern in pattern.findall(code):
            if (pattern != "") and (pattern not in filtered_pattern):
                filtered_pattern.append(pattern)

        return filtered_pattern

    def javascript_autocomplete(self):
        pass
