import re
from fridacli.logger import Logger

logger = Logger()

def extract_functions_python(code):
    def get_function_line(code, function):
        for id, line in enumerate(code, 1):
            if function.strip() in line:
                return id
    
    full_code = "".join(code)
    code_pattern = re.compile(r"(\s*def\s*([\w_]*)\s*\([\s\w:._,=\[\]]*\)\s*(?:->\s*[\w.\[\]]*)*\s*:\s*)", re.DOTALL)
    matches = code_pattern.findall(full_code)
    functions = []

    for id, match in enumerate(matches, 0):
        full_function = ""
        start = get_function_line(code, match[0])
        tabs = code[start - 1].rstrip().count("    ")
        next_lines = code[start + 1:]
        i = 0
        end = None

        for line in next_lines:
            line_tabs = line.rstrip().count("    ")
            if ("def" in line or line.strip() != "") and line_tabs <= tabs:
                end = start + i + 1
                break
            i += 1 
            full_function += line

        if end is None:
            end = len(code)

        functions.append({
            "order": id,
            "start_line": start,
            "end_line": end,
            "name_of_function": match[1],
            "code": match[0] + full_function,
        })

    return functions

def extract_functions_csharp(code):
    functions = []
    current_function = None
    current_function_lines = []
    brace_count = 0
    order = 0
    start_line = 0

    for idx, line in enumerate(code, 1):
        line = line.strip()

        # Check if it's a function definition
        function_match = re.match(
            r"^\s*(?:(?:public|private|protected|internal|static|async|unsafe|sealed|new|override|virtual|abstract)\s+)+([\w<>\[\],\.]+\s+)+([\w_]+)\s*\((.*)\)\s*(?:where.*)?\s*$",
            line,
        )
        if function_match:
            order += 1
            start_line = idx
            return_type = function_match.group(1)
            function_name = function_match.group(2)
            # logger.info(__name__, f"line: {idx} Return: {function_match.group(1)} Name: {function_match.group(2)} Args: {function_match.group(3)}")
            current_function = function_name
            current_function_lines = [line]
            brace_count = 1 if line.endswith("{") else 0
            continue

        # If inside a function, add lines to its list
        if current_function:
            current_function_lines.append(line)
            brace_count += line.count("{")
            brace_count -= line.count("}")

        # Check if the function ends
        if brace_count == 0 and current_function:
            functions.append(
                {
                    "order": order,
                    "start_line": start_line,
                    "end_line": idx,
                    "name_of_function": current_function,
                    "code": "\n".join(current_function_lines),
                }
            )
            current_function = None
            current_function_lines = []
    return functions


def extract_documentation_python(information, one_function, funct_name):
    lines = []
    first_parameter = True
    first_return = True
    first_exception = True

    try:
        if one_function:
            pass
        else:
            code_pattern = re.compile(
                r"(?:(?:.*)\s*class\s*([\w_\d]*)\s*:\s*(?:\"\"\"([\w\d\s\(\).#,:]*)\"\"\")*\s*)",
                re.DOTALL,
            )
            matches = code_pattern.findall(information["code"])
            for match in matches:
                lines.extend(
                    [
                        ("subheader", f"Class: {match[0]}"),
                        ("bold", "Description:"),
                        (
                            "text",
                            (
                                information["description"].strip()
                                if information["description"].strip()
                                else match[1].strip()
                            ),
                        ),
                    ]
                )

            code_pattern = re.compile(
                r"(?:\s*def\s*([\w\d_]*)\s*\(\s*(?:[\w,:\d_\s]*)\s*\)\s*(?:-\s*>\s*[\w.]*)*\s*:\s*(?:\"\"\"([\w\(\):.,`\s]*)\"\"\"))",
                re.DOTALL,
            )
            matches = code_pattern.findall(information["code"])

            for match in matches:
                funct_name = match[0]
                doc = match[1].split("\n\n")

                lines.append(("subheader", f"Function: {funct_name}"))
                lines.extend([("bold", "Description:"), ("text", doc[0].strip())])

                if len(doc) >= 2:
                    for line in doc[1:]:
                        sep = line.split("\n")
                        if "Args:" in sep[0]:
                            for arg in sep[1:]:
                                if "None" not in arg and arg.strip() != "":
                                    if first_parameter:
                                        lines.append(("bold", "Arguments:"))
                                        first_parameter = False
                                    if ":" in arg:
                                        sep_arg = arg.strip().split(":")
                                        lines.append(
                                            ("bullet", f"{sep_arg[0]}. {sep_arg[1]}")
                                        )
                                    else:
                                        sep_arg = arg.strip()
                                        lines[-1][1] += sep_arg
                        if "Returns:" in sep[0]:
                            for ret in sep[1:]:
                                if "None" not in ret and ret.strip() != "":
                                    if first_return:
                                        lines.append(("bold", "Returns:"))
                                        first_return = False
                                    if ":" in ret:
                                        sep_ret = ret.strip().split(":")
                                        lines.append(
                                            ("bullet", f"{sep_ret[0]}. {sep_ret[1]}")
                                        )
                                    else:
                                        sep_ret = ret.strip()
                                        lines[-1][1] += sep_ret
                        if "Raises:" in sep[0]:
                            for rai in sep[1:]:
                                if "None" not in rai and rai.strip() != "":
                                    if first_exception:
                                        lines.append(("bold", "Raises:"))
                                        first_exception = False
                                    if ":" in rai:
                                        sep_rai = rai.strip().split(":")
                                        lines.append(
                                            ("bullet", f"{sep_rai[0]}. {sep_rai[1]}")
                                        )
                                    else:
                                        sep_rai = rai.strip()
                                        lines[-1][1] += sep_rai
                first_parameter = True
                first_return = True
                first_exception = True

            return lines
    except Exception as e:
        logger.info(__name__, f"{e}")


def extract_documentation_csharp(information, one_function, funct_name):
    lines = []
    first_parameter = True
    first_return = True
    first_exception = True

    if one_function:
        lines = [("subheader", f"Function: {funct_name}")]
        if information["description"].rstrip() != "":
            lines.extend(
                [
                    ("bold", "Description:"),
                    ("text", information["description"].rstrip()),
                ]
            )

        for idx, line in enumerate(information["code"].splitlines(), 1):
            try:
                param_match = re.match(
                    r"^\s*///\s*<\s*param\s*name\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</param>\s*$",
                    line,
                )
                returns_match = re.match(
                    r"^\s*///\s*<\s*returns\s*>([\w\.\-\s<>=\"/{}]*)</returns>\s*$",
                    line,
                )
                exception_match = re.match(
                    r"^\s*///\s*<\s*exception\s*cref\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</exception>\s*$",
                    line,
                )

                if param_match:
                    if first_parameter:
                        lines.append(("bold", "Arguments:"))
                        lines.append(
                            (
                                "bullet",
                                f"{param_match.group(1)}. {param_match.group(2)}",
                            )
                        )
                        first_parameter = False
                    else:
                        lines.append(
                            (
                                "bullet",
                                f"{param_match.group(1)}. {param_match.group(2)}",
                            )
                        )

                elif returns_match:
                    if first_return:
                        lines.append(("bold", "Return:"))
                        lines.append(("bullet", f"{returns_match.group(1)}"))
                        first_return = False
                    else:
                        lines.append(("bullet", f"{returns_match.group(1)}"))
                elif exception_match:
                    if first_exception:
                        lines.append(("bold", "Exception:"))
                        lines.append(
                            (
                                "bullet",
                                f"{exception_match.group(1)}. {exception_match.group(2)}",
                            )
                        )
                        first_exception = False
                    else:
                        lines.append(
                            (
                                "bullet",
                                f"{exception_match.group(1)}. {exception_match.group(2)}",
                            )
                        )

            except Exception as e:
                logger.error(
                    __name__,
                    f"func: {function['name_of_function']} | idx: {idx} | line: {line} error: {e}",
                )
    else:
        function = []
        for idx, line in enumerate(information["code"].splitlines(), 1):
            try:
                param_match = re.match(
                    r"^\s*///\s*<\s*param\s*name\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</param>\s*$",
                    line,
                )
                returns_match = re.match(
                    r"^\s*///\s*<\s*returns\s*>([\w\.\-\s<>=\"/{}]*)</returns>\s*$",
                    line,
                )
                exception_match = re.match(
                    r"^\s*///\s*<\s*exception\s*cref\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</exception>\s*$",
                    line,
                )
                function_match = re.match(
                    r"^\s*(?:(?:public|private|protected|internal|static|async|unsafe|sealed|new|override|virtual|abstract)\s+)+(?:[\w<>\[\],\.]+\s+)+([\w_]+)\s*\((?:.*)\)\s*(?:where.*)?\s*$",
                    line,
                )

                if param_match:
                    if first_parameter:
                        function.append(("bold", "Arguments:"))
                        function.append(
                            (
                                "bullet",
                                f"{param_match.group(1)}. {param_match.group(2)}",
                            )
                        )
                        first_parameter = False
                    else:
                        function.append(
                            (
                                "bullet",
                                f"{param_match.group(1)}. {param_match.group(2)}",
                            )
                        )

                elif returns_match:
                    if first_return:
                        function.append(("bold", "Return:"))
                        function.append(("bullet", f"{returns_match.group(1)}"))
                        first_return = False
                    else:
                        function.append(("bullet", f"{returns_match.group(1)}"))
                elif exception_match:
                    if first_exception:
                        function.append(("bold", "Exception:"))
                        function.append(
                            (
                                "bullet",
                                f"{exception_match.group(1)}. {exception_match.group(2)}",
                            )
                        )
                        first_exception = False
                    else:
                        function.append(
                            (
                                "bullet",
                                f"{exception_match.group(1)}. {exception_match.group(2)}",
                            )
                        )
                elif function_match:
                    lines.extend(
                        [("subheader", f"Function: {function_match.group(1)}")]
                    )
                    if information["description"].rstrip() != "":
                        lines.extend(
                            [
                                ("bold", "Description:"),
                                ("text", information["description"].rstrip()),
                            ]
                        )
                    lines.extend(function)

                    function = []
                    first_parameter = True
                    first_return = True
                    first_exception = True

            except Exception as e:
                logger.error(__name__, f"idx: {idx} | line: {line} error: {e}")

    return lines
