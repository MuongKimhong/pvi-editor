import subprocess
import os

import re


class AutoComplete:
    def __init__(self, main_editor: "MainEditor") -> None:
        self.language = None
        self.suggestion = {}
    
    def filter_pattern(self, patterns: list) -> list:
        filtered_pattern = []

        for pattern in patterns:
            if (pattern != "") and (pattern not in filtered_pattern):
                filtered_pattern.append(pattern)

        return filtered_pattern

    def get_suggestion(self, code) -> list:
        if self.language == "python":
            return self.python_autocomplete(code)
        elif self.language == "javascript":
            return self.javascript_autocomplete(code)
        elif self.language == "typescript":
            return self.typescript_autocomplete(code)
        elif self.language == "html":
            return self.html_autocomplete(code)
    
    def python_autocomplete(self, code):
        patterns = re.compile(r'\b(?:def|class|from|import|([a-zA-Z_]\w*)\s*\(.*?\))')
        return self.filter_pattern(patterns=patterns.findall(code))

    def javascript_autocomplete(self, code):
        variable_pattern = re.compile(r'\bvar\s+([a-zA-Z_]\w*)\s*=')
        function_pattern = re.compile(r'\bfunction\s+([a-zA-Z_]\w*)\s*\(')
        import_pattern = re.compile(r'\bimport\s+{[^}]+}\s+from\s+[\'"]([^\'"]+)[\'"]')
        class_pattern = re.compile(r'\bclass\s+([a-zA-Z_]\w*)\s*[{]?')
        
        variables = variable_pattern.findall(code)
        functions = function_pattern.findall(code)
        imports = import_pattern.findall(code)
        classes = class_pattern.findall(code)

        return self.filter_pattern([*variables, *functions, *imports, *classes])

    # def rust_autocomplete(self, code):
    #     pattern = re.compile(
    #         r'\b(?:let\s+([a-zA-Z_]\w*)\s*=\s*|fn\s+([a-zA-Z_]\w*)\s*\(|use\s+[\w:]+::([a-zA-Z_]\w*)\s*;|struct\s+([a-zA-Z_]\w*)\s*[{])'
    #     )
    #     patterns = pattern.findall(code)
    #     let_rust, fn_rust, use_rust, struct_rust = zip(*patterns)

    #     variables = [v for v in let_rust if v]
    #     functions = [f for f in fn_rust if f]
    #     structs = [s for s in struct_rust if s]

    #     return self.filter_pattern([*variables, *functions, *structs])

    def html_autocomplete(self, code):
        pre_defined_tags = [
            "<audio></audio>", "<canvas></canvas>", "<b></b>", "<body></body>", 
            "<dir></dir>", "<div></div>", "<dl></dl>", "<dt></dt>", "<form></form>",
            "<head></head>", "<legend></legend>", "<link></link>", "<hr>", "<i></i>",
            "<input>", "<html></html>", "<h1></h1>", "<h2></h2>", "<h3></h3>", "<h4></h4>",
            "<h5></h5>", "<h6></h6>", "<p></p>", "<img>", "<script src=''></script>", "<ol></ol>"
        ]
        return pre_defined_tags

    # def php_autocomplete(self, code):
    #     pattern_php = re.compile(r'\b(?:function\s+([a-zA-Z_]\w*)\s*\(|class\s+([a-zA-Z_]\w*)\s*[{])')
    #     patterns = pattern_php.findall(code)
    #     function_php, class_php = zip(*patterns)

    #     functions = [f for f in function_php if f]
    #     classes = [c for c in class_php if c]
    #     variables = re.compile(r'\$([a-zA-Z_]\w*)\s*=\s*').findall(code)

    #     return self.filter_pattern([*functions, *classes, *variables])

    def typescript_autocomplete(self, code):
        pattern_ts = re.compile(
            r'\b(?:let\s+([a-zA-Z_]\w*)\s*:\s*|function\s+([a-zA-Z_]\w*)\s*\(|import\s+{[^}]+}\s+from\s+[\'"]([^\'"]+)[\'"]|class\s+([a-zA-Z_]\w*)\s*[{]?)'
        )
        patterns = pattern_ts.findall(code)
        variable_ts, function_ts, imports_ts, class_ts = zip(*patterns)

        patterns = [
            *[v for v in variable_ts if v],
            *[f for f in function_ts if f],
            *[i for i in imports_ts if i],
            *[c for c in class_ts if c]
        ]
        return self.filter_pattern(patterns)

    # def c_autocomplete(self, code):
    #     pattern_c = re.compile(
    #         r'\b(?:int\s+([a-zA-Z_]\w*)\s*=\s*|void\s+([a-zA-Z_]\w*)\s*\(|printf\s*\(\s*"([^"]+)"\s*\)\s*;|}\s*([a-zA-Z_]\w*)\s*[{]?)'
    #     )
    #     matches_c = pattern_c.findall(code)
    #     variable_c, function_c, printf_c, class_c = zip(*matches_c)
    #     patterns = [
    #         *[v for v in variable_c if v],
    #         *[f for f in function_c if f],
    #         *[p for p in printf_c if p],
    #         *[c for c in class_c if c]
    #     ]
    #     return self.filter_pattern(patterns)

    # def cpp_autocomplete(self, code):
    #     pattern_cpp_variables = re.compile(r'\b(?:int\s+|double\s+|std::\w+\s+)\s*([a-zA-Z_]\w*)\s*=\s*')
    #     pattern_cpp_functions = re.compile(r'\b(?:void\s+|[a-zA-Z_]\w+\s+([a-zA-Z_]\w*)\s*\([^)]*\))')
    #     pattern_cpp_classes = re.compile(r'\bclass\s+([a-zA-Z_]\w*)\s*[{]?')
    #     pattern_cpp_includes = re.compile(r'#include\s+[<"]([^>"]+)[>"]')

    #     matches_cpp_variables = pattern_cpp_variables.findall(code)
    #     matches_cpp_functions = pattern_cpp_functions.findall(code)
    #     matches_cpp_classes = pattern_cpp_classes.findall(code)
    #     matches_cpp_includes = pattern_cpp_includes.findall(code)

    #     # Extract and print the matched entities
    #     variables = [var for var in matches_cpp_variables]
    #     functions = [func for func in matches_cpp_functions]
    #     classes = [cls for cls in matches_cpp_classes]
    #     includes = [include for include in matches_cpp_includes]

    #     return self.filter_pattern([*variables, *functions, *classes, *includes])
