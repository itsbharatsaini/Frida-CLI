import re
from fridacli.logger import Logger
from .regex_configuration import (
    DOCUMENTATION_FROM_ALL_FUNCTIONS_PYTHON,
    DEFINITION_OF_FUNCTION_PYTHON,
    PARAM_CSHARP,
    RETURN_CSHARP,
    EXCEPTION_CSHARP,
)

logger = Logger()


def extract_functions_python(code):
    def get_function_line(code, function):
        for id, line in enumerate(code, 1):
            if function.strip().split("    ")[0] in line:
                return id

    full_code = "".join(code)
    code_pattern = re.compile(
        DEFINITION_OF_FUNCTION_PYTHON,
        re.DOTALL,
    )
    matches = code_pattern.findall(full_code)
    functions = []

    for id, match in enumerate(matches, 0):
        full_function = ""
        start = get_function_line(code, match[0])
        tabs = code[start - 1].rstrip().count("    ")
        additional_lines = match[0].strip().count("    ") + 1
        next_lines = code[start + additional_lines :]
        i = 0
        end = None

        for line in next_lines:
            line_tabs = line.rstrip().count("    ")
            if ("def" in line or line.strip() != "") and line_tabs <= tabs:
                end = start + i + additional_lines
                break
            i += 1
            full_function += line

        if end is None:
            end = len(code)

        functions.append(
            {
                "order": id,
                "start_line": start,
                "end_line": end,
                "name_of_function": match[1],
                "code": match[0] + full_function,
            }
        )
        # logger.info(__name__, functions[-1])

    return functions


def extract_documentation_python(information, one_function, funct_name):
    lines = []
    first_parameter = True
    first_return = True
    first_exception = True
    first_function = True

    try:
        if not one_function:
            if information["description"].strip() != "":
                lines.extend(
                    [
                        ("bold", "Description:"),
                        ("text", information["description"].strip()),
                    ]
                )

        code_pattern = re.compile(
            DOCUMENTATION_FROM_ALL_FUNCTIONS_PYTHON,
            re.DOTALL,
        )

        matches = code_pattern.findall(information["code"])

        logger.info(__name__, f"Matches found: {matches}")

        for match in matches:
            funct_name = match[1]
            doc = match[2] if first_function else (match[0] or match[2])

            if doc != "":
                doc = doc.replace("\n    \n", "\n\n")
                doc = doc.split("\n\n")
                lines.append(("subheader", f"Function: {funct_name}"))

                if doc[0].strip() != "":
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
                                        sep_arg = arg.strip().split(":", 1)
                                        if sep_arg[1] != "" and "-" not in sep_arg[0]:
                                            lines.append(
                                                (
                                                    "bullet",
                                                    f"{sep_arg[0]}. {sep_arg[1]}",
                                                )
                                            )
                                        else:
                                            sep_arg = arg.strip()
                                            lines[-1] = (
                                                lines[-1][0],
                                                lines[-1][1] + "\n" + arg.strip(),
                                            )
                                    else:
                                        sep_arg = arg.strip()
                                        lines[-1] = (
                                            lines[-1][0],
                                            lines[-1][1] + "\n" + arg.rstrip(),
                                        )
                        elif "Returns:" in sep[0]:
                            for ret in sep[1:]:
                                if "None" not in ret and ret.strip() != "":
                                    if first_return:
                                        lines.append(("bold", "Returns:"))
                                        first_return = False
                                    if ":" in ret:
                                        sep_ret = ret.strip().split(":", 1)
                                        if sep_ret[1] != "" and "-" not in sep_ret[0]:
                                            lines.append(
                                                (
                                                    "bullet",
                                                    f"{sep_ret[0]}. {sep_ret[1]}",
                                                )
                                            )
                                        else:
                                            sep_ret = ret.strip()
                                            lines[-1] = (
                                                lines[-1][0],
                                                lines[-1][1] + "\n" + ret.rstrip(),
                                            )
                                    else:
                                        sep_ret = ret.strip()
                                        lines[-1] = (
                                            lines[-1][0],
                                            lines[-1][1] + "\n" + ret.rstrip(),
                                        )
                        elif "Raises:" in sep[0]:
                            for rai in sep[1:]:
                                if "None" not in rai and rai.strip() != "":
                                    if first_exception:
                                        lines.append(("bold", "Raises:"))
                                        first_exception = False
                                    if ":" in rai:
                                        sep_rai = rai.strip().split(":", 1)
                                        if sep_rai[1] != "" and "-" not in sep_rai[0]:
                                            lines.append(
                                                (
                                                    "bullet",
                                                    f"{sep_rai[0]}. {sep_rai[1]}",
                                                )
                                            )
                                        else:
                                            sep_rai = rai.strip()
                                            lines[-1] = (
                                                lines[-1][0],
                                                lines[-1][1] + "\n" + rai.rstrip(),
                                            )
                                    else:
                                        sep_rai = rai.strip()
                                        lines[-1] = (
                                            lines[-1][0],
                                            lines[-1][1] + "\n" + rai.rstrip(),
                                        )
                        elif (
                            first_parameter
                            and first_return
                            and first_exception
                            and line.strip() != ""
                        ):
                            lines[2] = (
                                "text",
                                lines[2][1] + "\n" + line.strip().replace("    ", ""),
                            )

                first_parameter = True
                first_return = True
                first_exception = True

            if one_function:
                break

        return lines
    except Exception as e:
        logger.info(__name__, f"{e}")


def extract_doc_csharp(comments):
    first_parameter = True
    first_return = True
    first_exception = True
    start = comments.find("<summary>")
    end = comments.find("</summary>")
    description = comments[start + 9 : end]
    comments = comments[end + 10 + 1 :]

    if description != "":
        lines = [
            ("bold", "Description:"),
            ("text", description.strip()),
        ]
    else:
        lines = []

    logger.info(__name__, comments.splitlines())

    for comment in comments.splitlines():
        try:
            param_match = re.match(
                PARAM_CSHARP,
                comment,
            )
            returns_match = re.match(
                RETURN_CSHARP,
                comment,
            )
            exception_match = re.match(
                EXCEPTION_CSHARP,
                comment,
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
            logger.error(__name__, e)

    return lines


def find_all_func_csharp(node):
    comments, definition, class_defintion = (
        "",
        "",
        "",
    )
    start, end = -1, -1
    functions, classes = [], []

    for n in node.children:
        if node.type == "declaration_list":
            if n.type == "class_declaration":
                for data in n.children:
                    if data.type == "identifier":
                        class_defintion += data.text.decode("utf8") + " "
                        class_name = data.text.decode("utf8")
                    elif data.type != "declaration_list":
                        class_defintion += data.text.decode("utf8") + " "
                    else:
                        classes.append(
                            {"name": class_name, "definition": class_defintion}
                        )
                        class_name = ""
                        class_defintion = ""
            if n.type == "comment":
                comments += n.text.decode("utf8") + "\n"
                if start == -1:
                    start = n.range.start_byte
                end = n.range.end_byte
            if n.type == "method_declaration" or n.type == "constructor_declaration":
                for data in n.children:
                    if data.type == "block":
                        body = data.text.decode("utf8")
                        functions.append(
                            {
                                "name": name,
                                "definition": definition,
                                "body": body,
                                "comments": comments,
                                "range": (n.range.start_byte, n.range.end_byte),
                                "comments_range": (start, end),
                            }
                        )
                        (
                            comments,
                            definition,
                            class_defintion,
                        ) = ("", "", "")
                        start, end = -1, -1
                    elif data.type == "identifier":
                        definition += data.text.decode("utf8") + " "
                        name = data.text.decode("utf8")
                    else:
                        definition += data.text.decode("utf8") + " "
        if n.children != []:
            f, c = find_all_func_csharp(n)
            if f != []:
                functions.extend(f)
            if c != []:
                classes.extend(c)
    return functions, classes


def extract_doc_csharp_all_func(node):
    docs = []

    functions, classes = find_all_func_csharp(node)

    for func in functions:
        name = func["name"]
        comments = func["comments"]
        logger.info(__name__, f"func: {name}, comments: {comments}")
        documentation = extract_doc_csharp(comments.replace("///", ""))
        if documentation != []:
            docs.append(("subheader", f"Function: {name}"))
            docs.extend(documentation)

    return docs


def extract_doc_csharp_one_func(node, name):
    comments = ""
    lines = [("subheader", f"Function: {name}")]

    for n in node.children:
        if n.type == "comment":
            comments += n.text.decode("utf8") + "\n"
    logger.info(__name__, comments)
    lines.extend(extract_doc_csharp(comments.replace("///", "")))

    return lines
