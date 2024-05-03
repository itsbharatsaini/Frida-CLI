import re
from fridacli.logger import Logger

logger = Logger()


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
