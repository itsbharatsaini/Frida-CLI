import re
from typing import Tuple, List
from tree_sitter import Tree
from fridacli.logger import Logger
from .regex_configuration import (
    PARAM_CSHARP,
    RETURN_CSHARP,
    EXCEPTION_CSHARP,
    PARAM_JAVA,
    RETURN_JAVA,
    EXCEPTION_JAVA,
    DESCRIPTION_JAVA,
)

logger = Logger()

# Documentacion Java


def extract_doc_java(comments: str) -> Tuple[List, str | None]:
    """
    Extracts documentation from Java-style comments.

    Args:
        comments (str): The string containing the Java-style comments.

    Returns:
        Tuple[List, str | None]: A tuple containing the extracted documentation as a list of formatted lines and an optional error message.
    """
    lines = []
    first_parameter = True
    first_return = True
    first_exception = True
    first_description = True

    try:
        for line in comments.splitlines():
            if line.replace("*", "").strip() != "":
                # Check if the current string refers to description, arguments, return values or exception
                description_match = re.match(DESCRIPTION_JAVA, line)
                param_match = re.match(PARAM_JAVA, line)
                returns_match = re.match(RETURN_JAVA, line)
                exception_match = re.match(EXCEPTION_JAVA, line)

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
                elif description_match:
                    if first_description:
                        lines.append(("bold", "Description:"))
                        lines.append(("text", f"{description_match.group(1)}"))
                        first_description = False
                    else:
                        # If not first description line, add the line to the description tuple
                        lines[-1] = (
                            "text",
                            lines[-1][1] + "\n" + description_match.group(1),
                        )
    except Exception as e:
        logger.error(__name__, f"(extract_doc_java) {e}")
        # If somethin went wrong, an empty list and the error is returned
        return [], e
    else:
        # If everything went right, the documentation and no errors are returned
        return lines, None


def find_all_func_java(node: Tree, file_name: str):
    """
    Recursively finds all function and class definitions in a Java code tree.

    Args:
        node (Tree): The root node of the Java code tree.
        file_name (str): The name of the file that contains the functions.

    Returns:
        tuple: A list of dictionaries representing function definitions, each with the following keys:
                - "name" (str): The name of the function.
                - "definition" (str): The definition of the function.
                - "body" (str): The body of the function.
                - "range" (tuple[int, int]): The start and end byte range of the function.
                - "comments" (str): The comments associated with the function definition.
                - "comments_range" (tuple[int, int]): The start and end byte range of the comments.
               A list of dictionaries representing class definitions, each with the following keys:
                - "name" (str): The name of the class.
                - "definition" (str): The definition of the class.
    Raises:
        Exception: If an error occurs during processing.
    """
    definition, class_defintion, comments, name = "", "", "", ""
    functions, classes = [], []
    range = None

    try:
        for n in node.children:
            # Extract information from a class
            if n.type == "class_declaration":
                for data in n.children:
                    if data.type == "class_body":
                        classes.append(
                            {"name": class_name, "definition": class_defintion}
                        )
                        class_defintion, class_name = "", ""
                    elif data.type == "identifier":
                        class_defintion += data.text.decode("utf8")
                        class_name = data.text.decode("utf8")
                    else:
                        class_defintion += data.text.decode("utf8")
                        class_defintion += " "
            # Extract information from a comment block
            if n.type == "block_comment":
                if comments == "":
                    comments = n.text.decode("utf8")
                    if "/**" in comments:
                        range = (n.range.start_byte, n.range.end_byte)
                    else:
                        comments = ""
            # Extract information from a method
            if n.type == "method_declaration":
                for data in n.children:
                    if data.type == "block":
                        body = data.text.decode("utf8")
                        functions.append(
                            {
                                "name": name,
                                "definition": definition,
                                "body": body,
                                "range": (n.range.start_byte, n.range.end_byte),
                                "comments": comments,
                                "comments_range": range,
                            }
                        )
                        definition, comments = "", ""
                        range = None
                    elif data.type == "identifier":
                        definition += data.text.decode("utf8")
                        name = data.text.decode("utf8")
                    else:
                        definition += data.text.decode("utf8")
                        definition += " "
            # Call the function using the current node as the root
            if n.children != []:
                f, c = find_all_func_java(n, file_name)
                if f != []:
                    functions.extend(f)
                if c != []:
                    classes.extend(c)
    except Exception as e:
        # If something went wrong, only empty lists are returned
        logger.error(__name__, f"(find_all_func_java) {e}")
        return [], []
    else:
        # logger.info(
        #     __name__,
        #     f"(find_all_func_java) Successfully extracted all the function from the file {file_name}",
        # )
        return functions, classes


def extract_doc_java_all_func(node: Tree, file_name: str):
    """
    Extracts documentation from all functions in a Java abstract syntax tree.

    Args:
        node (Tree): The abstract syntax tree node representing the Java code.
        file_name (str): The name of the file that contains the functions.

    Returns:
        tuple: A tuple consisting of two lists. The first list contains the extracted documentation, organized as a list of tuples.
               The second list contains any encountered errors while extracting the documentation from the functions.
    """
    docs, errors = [], {}

    functions, classes = find_all_func_java(node, file_name)
    total = len(functions)
    documented = 0

    for func in functions:
        funct_definition = func["definition"]
        comments = func["comments"]
        if comments != "":
            logger.info(
                __name__,
                f"(extract_doc_java_all_func) Comments retrieved from the function {funct_definition}: {comments}",
            )
            documentation, error = extract_doc_java(
                comments.replace("*/", "").replace("/**", "")
            )
            if error is None:
                logger.info(
                    __name__,
                    f"(extract_doc_java_all_func) Successfully extracted the documentation for the function {funct_definition}",
                )
                docs.append(("subheader", f"Function: {funct_definition}"))
                docs.extend(documentation)
                documented += 1
            else:
                # If something went wrong while extracting the documentation from the comments
                logger.error(
                    __name__,
                    f"(extract_doc_java_all_func) Could't extract the documentation from the function {funct_definition}",
                )
                errors.update(
                    {
                        funct_definition: "Could't extract the documentation from the function."
                    }
                )
        else:
            # If comments weren't found
            logger.error(
                __name__,
                f"(extract_doc_java_all_func) Could't extract the comments from the function {funct_definition}.",
            )
            errors.update(
                {funct_definition: "Could't extract the comments from the function."}
            )
    return docs, errors, (total, documented)


def extract_doc_java_one_func(node: Tree, funct_definition: str):
    """
    Extracts the documentation from a Java function.

    Args:
        node (Tree): The tree representing the Java function.
        funct_definition (str): The definition (name, args, return value) of the Java function.

    Returns:
        tuple: A list containing the extracted documentation as tuples.
               A dictionary containing the error message if a problem occurred during extraction, otherwise None.
    """
    comments = ""
    error = None
    docs = []

    try:
        for n in node.children:
            if n.type == "block_comment":
                comments = n.text.decode("utf8")
                break
        if comments != "":
            logger.info(
                __name__,
                f"(extract_doc_java_one_func) Comments retrieved from the function {funct_definition}: {comments}",
            )
            documentation, error = extract_doc_java(
                comments.replace("*/", "").replace("/**", "")
            )
            if error is None:
                logger.info(
                    __name__,
                    f"(extract_doc_java_one_func) Successfully extracted the documentation for the function {funct_definition}",
                )
                docs.append(("subheader", f"Function: {funct_definition}"))
                docs.extend(documentation)
            else:
                logger.error(
                    __name__,
                    f"(extract_doc_java_one_func) Could't extract the documentation from the function {funct_definition}",
                )
                error = {
                    funct_definition: "Could't extract the documentation from the function."
                }
        else:
            # If comments weren't found
            logger.error(
                __name__,
                f"(extract_doc_java_one_func) Could't extract the comments from the function {funct_definition}",
            )
            error = {
                funct_definition: "Could't extract the comments from the function."
            }
    except Exception as e:
        logger.error(__name__, f"(extract_doc_java_one_func) {e}")

    return docs, error


# Documentacion Python


def extract_doc_python(comments: str) -> Tuple[List, str | None]:
    """
    Extracts and formats documentation from a comments string.

    Args:
        comments (str): The comments string containing the function documentation.

    Returns:
        Tuple[List, str | None]: A tuple containing the extracted documentation as a list of formatted lines and an optional error message.

    """
    lines = []
    first_parameter = True
    first_return = True
    first_exception = True

    try:
        doc = comments.replace("\n    \n", "\n\n")
        doc = doc.split("\n\n")

        logger.info(__name__, f"(extract_doc_python) Comment lines: {doc}")

        if doc[0].strip() != "":
            lines.extend([("bold", "Description:"), ("text", doc[0].strip())])

        if len(doc) >= 2:
            for line in doc[1:]:
                sep = line.split("\n")
                if "Args:" in sep[0]:
                    # If Args: in line, save all the argument lines listed
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
                    # If Returns: in line, save all the return lines listed
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
                    # If Raises: in line, save all the exception lines listed
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
                    # If not found a paramater, return value or exception, add the line to the description tuple
                    lines[-1] = (
                        "text",
                        lines[-1][1] + "\n" + line.strip().replace("    ", ""),
                    )
    except Exception as e:
        logger.error(__name__, f"(extract_doc_python) {e}")
        # If somethin went wrong, an empty list and the error is returned
        return [], e
    else:
        # If everything went right, the documentation and no errors are returned
        return lines, None


def find_all_func_python(node: Tree, file_name: str):
    """
    Recursively finds all function and class definitions in a Python code tree.

    Args:
        node (Tree): The root node of the Python code tree.
        file_name (str): The name of the file that contains the functions.

    Returns:
        tuple: A list of dictionaries representing function definitions, each with the following keys:
                - "name" (str): The name of the function.
                - "definition" (str): The definition of the function.
                - "body" (str): The body of the function.
                - "range" (tuple[int, int]): The start and end byte range of the function.
                - "comments" (str): The comments associated with the function definition.
                - "comments_range" (tuple[int, int]): The start and end byte range of the comments.
               A list of dictionaries representing class definitions, each with the following keys:
                - "name" (str): The name of the class.
                - "definition" (str): The definition of the class.
    Raises:
        Exception: If an error occurs during processing.
    """
    definition, class_defintion = "", ""
    functions, classes = [], []

    try:
        for n in node.children:
            # Extract information from a class
            if n.type == "class_definition":
                for data in n.children:
                    if data.type == "block":
                        classes.append(
                            {"name": class_name, "definition": class_defintion}
                        )
                        class_defintion, class_name = "", ""
                    elif data.type == "identifier":
                        class_defintion += data.text.decode("utf8")
                        class_name = data.text.decode("utf8")
                    else:
                        class_defintion += data.text.decode("utf8")
                        class_defintion += (
                            " "
                            if (data.type != ":" and data.type != "parameters")
                            else ""
                        )
            # Extract information from a method
            if n.type == "function_definition":
                for data in n.children:
                    if data.type == "block":
                        body = data.text.decode("utf8")
                        temp = data.children[0].text.decode("utf8")
                        # Extract information from a comment block
                        comments, range = (
                            (
                                temp,
                                (
                                    data.children[0].range.start_byte,
                                    data.children[0].range.end_byte,
                                ),
                            )
                            if '"""' in temp
                            else ("", ())
                        )
                        functions.append(
                            {
                                "name": name,
                                "definition": definition,
                                "body": body,
                                "range": (n.range.start_byte, n.range.end_byte),
                                "comments": comments,
                                "comments_range": range,
                            }
                        )
                        definition = ""
                    elif data.type == "identifier":
                        definition += data.text.decode("utf8")
                        name = data.text.decode("utf8")
                    elif data.type != "comment":
                        definition += data.text.decode("utf8")
                        definition += (
                            " "
                            if (data.type != ":" and data.type != "parameters")
                            else ""
                        )
            # Call the function using the current node as the root
            if n.children != []:
                f, c = find_all_func_python(n, file_name)
                if f != []:
                    functions.extend(f)
                if c != []:
                    classes.extend(c)
    except Exception as e:
        # If something went wrong, only empty lists are returned
        logger.error(__name__, f"(find_all_func_python) {e}")
        return [], []
    else:
        # logger.error(
        #     __name__,
        #     f"(find_all_func_python) Successfully extracted all the function from the file {file_name}",
        # )
        return functions, classes


def extract_doc_python_all_func(node: Tree, file_name: str):
    """
    Extracts documentation from all functions in a Python abstract syntax tree.

    Args:
        node (Tree): The abstract syntax tree node representing the Python code.
        file_name (str): The name of the file that contains the functions.

    Returns:
        tuple: A tuple consisting of two lists. The first list contains the extracted documentation, organized as a list of tuples.
               The second list contains any encountered errors while extracting the documentation from the functions.
    """
    docs, errors = [], {}

    functions, classes = find_all_func_python(node, file_name)
    total = len(functions)
    documented = 0

    for func in functions:
        funct_definition = func["definition"]
        comments = func["comments"]
        if comments != "":
            logger.info(
                __name__,
                f"(extract_doc_python_all_func) comments retrieved from the function {funct_definition}: {comments}",
            )
            documentation, error = extract_doc_python(comments.replace('"""', ""))
            if error is None:
                logger.info(
                    __name__,
                    f"(extract_doc_python_all_func) Successfully extracted the documentation for the function {funct_definition}",
                )
                docs.append(("subheader", f"Function: {funct_definition}"))
                docs.extend(documentation)
                documented += 1
            else:
                # If something went wrong while extracting the documentation from the comments
                logger.error(
                    __name__,
                    f"(extract_doc_python_all_func) Could't extract the documentation from the function {funct_definition}",
                )
                errors.update(
                    {
                        funct_definition: "Could't extract the documentation from the function."
                    }
                )
        else:
            # If comments weren't found
            logger.error(
                __name__,
                f"(extract_doc_python_all_func) Could't extract the comments from the function {funct_definition}.",
            )
            errors.update(
                {funct_definition: "Could't extract the comments from the function."}
            )
    return docs, errors, (total, documented)


def extract_doc_python_one_func(node: Tree, funct_definition: str):
    """
    Extracts the documentation from a Python function.

    Args:
        node (Tree): The tree representing the Python function.
        funct_definition (str): The definition (name, args, return values) of the Python function.

    Returns:
        tuple: A list containing the extracted documentation as tuples.
               A dictionary containing the error message if a problem occurred during extraction, otherwise None.
    """
    docs = []
    comments = ""
    error = None

    try:
        for n in node.children:
            # If the comments are above the method definition
            if n.type == "expression_statement":
                if '"""' in n.text.decode("utf8"):
                    comments = n.text.decode("utf8")
                    break
            # If the comments are below the method definition
            if n.type == "function_definition":
                for data in n.children[-1].children:
                    if data.type == "expression_statement":
                        comments = data.text.decode("utf8")
                        break
                break
        if '"""' in comments:
            logger.info(
                __name__,
                f"(extract_doc_python_one_func) comments retrieved from the function {funct_definition}: {comments}",
            )
            documentation, error = extract_doc_python(comments.replace('"""', ""))
            if error is None:
                logger.info(
                    __name__,
                    f"(extract_doc_python_one_func) Successfully extracted the documentation for the function {funct_definition}",
                )
                docs.append(("subheader", f"Function: {funct_definition}"))
                docs.extend(documentation)
            else:
                logger.error(
                    __name__,
                    f"(extract_doc_python_one_func) Could't extract the documentation from the function {funct_definition}",
                )
                error = {
                    funct_definition: "Could't extract the documentation from the function."
                }
        else:
            # If comments weren't found
            logger.error(
                __name__,
                f"(extract_doc_python_one_func) Could't extract the comments from the function.",
            )
            error = {
                funct_definition: "Could't extract the comments from the function."
            }
    except Exception as e:
        logger.error(__name__, f"(extract_doc_python_one_func) {e}")

    return docs, error


# Documentacion C#


def extract_doc_csharp(comments: str) -> Tuple[List, str | None]:
    """
    Extracts documentation from C#-style comments.

    Args:
        comments (str): The string containing the C#-style comments.

    Returns:
        Tuple[List, str | None]: A tuple containing the extracted documentation as a list of formatted lines and an optional error message.
    """
    first_parameter = True
    first_return = True
    first_exception = True

    try:
        # Extraction of the description
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

        logger.info(
            __name__, f"(extract_doc_csharp) Comment lines: {comments.splitlines()}"
        )

        for comment in comments.splitlines():
            # Check if the current string refers to description, arguments, return values or exception
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
        logger.error(__name__, f"(extract_doc_csharp) {e}")
        # If somethin went wrong, an empty list and the error is returned
        return [], e
    else:
        # If everything went right, the documentation and no errors are returned
        return lines, None


def find_all_func_csharp(node: Tree, file_name: str):
    """
    Recursively finds all function and class definitions in a C# code tree.

    Args:
        node (Tree): The root node of the C# code tree.
        file_name (str): The name of the file that contains the functions.

    Returns:
        tuple: A list of dictionaries representing function definitions, each with the following keys:
                - "name" (str): The name of the function.
                - "definition" (str): The definition of the function.
                - "body" (str): The body of the function.
                - "range" (tuple[int, int]): The start and end byte range of the function.
                - "comments" (str): The comments associated with the function definition.
                - "comments_range" (tuple[int, int]): The start and end byte range of the comments.
               A list of dictionaries representing class definitions, each with the following keys:
                - "name" (str): The name of the class.
                - "definition" (str): The definition of the class.
    Raises:
        Exception: If an error occurs during processing.
    """
    comments, definition, class_defintion = (
        "",
        "",
        "",
    )
    start, end = -1, -1
    functions, classes = [], []

    try:
        for n in node.children:
            if node.type == "compilation_unit":
                # Extract information from a comment block
                if n.type == "comment":
                    comments += n.text.decode("utf8") + "\n"
                    if start == -1:
                        start = n.range.start_byte
                    end = n.range.end_byte
                elif n.type == "global_statement":
                    for data in n.children[0].children:
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
            if node.type == "declaration_list":
                # Extract information from a class
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
                # Extract information from a comment block
                if n.type == "comment":
                    comments += n.text.decode("utf8") + "\n"
                    if start == -1:
                        start = n.range.start_byte
                    end = n.range.end_byte
                # Extract information from a method
                if (
                    n.type == "method_declaration"
                    or n.type == "constructor_declaration"
                ):
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
            # Call the function using the current node as the root
            if n.children != []:
                f, c = find_all_func_csharp(n, file_name)
                if f != []:
                    functions.extend(f)
                if c != []:
                    classes.extend(c)
    except Exception as e:
        # If something went wrong, only empty lists are returned
        logger.error(__name__, f"(find_all_func_csharp) {e}")
        return [], []
    else:
        # logger.info(
        #     __name__,
        #     f"(find_all_func_csharp) Successfully extracted all the function from the file {file_name}",
        # )
        return functions, classes


def extract_doc_csharp_all_func(node: str, file_name: str):
    """
    Extracts documentation from all functions in a C# abstract syntax tree.

    Args:
        node (Tree): The abstract syntax tree node representing the C# code.
        file_name (str): The name of the file that contains the functions.

    Returns:
        tuple: A tuple consisting of two lists. The first list contains the extracted documentation, organized as a list of tuples.
               The second list contains any encountered errors while extracting the documentation from the functions.
    """
    docs, errors = [], {}

    functions, classes = find_all_func_csharp(node, file_name)
    total = len(functions)
    documented = 0

    for func in functions:
        funct_definition = func["definition"]
        comments = func["comments"]
        if comments != "":
            logger.info(
                __name__,
                f"(extract_doc_csharp_all_func) comments retrieved from the function {funct_definition}: {comments}",
            )
            documentation, error = extract_doc_csharp(comments.replace("///", ""))
            if error is None:
                logger.info(
                    __name__,
                    f"(extract_doc_csharp_all_func) Successfully extracted the documentation for the function {funct_definition}",
                )
                docs.append(("subheader", f"Function: {funct_definition}"))
                docs.extend(documentation)
                documented += 1
            else:
                # If something went wrong while extracting the documentation from the comments
                logger.error(
                    __name__,
                    f"(extract_doc_csharp_all_func) Could't extract the documentation from the function {funct_definition}",
                )
                errors.update(
                    {
                        funct_definition: "Could't extract the documentation from the function."
                    }
                )
        else:
            # If comments weren't found
            logger.error(
                __name__,
                f"(extract_doc_csharp_all_func) Could't extract the comments from the function {funct_definition}.",
            )
            errors.update(
                {funct_definition: "Could't extract the comments from the function."}
            )
    return docs, errors, (total, documented)


def extract_doc_csharp_one_func(node: Tree, funct_definition: str):
    """
    Extracts the documentation from a C# function.

    Args:
        node (Tree): The tree representing the C# function.
        funct_definition (str): The definition (name, args, return values) of the C# function.

    Returns:
        tuple: A list containing the extracted documentation as tuples.
               A dictionary containing the error message if a problem occurred during extraction, otherwise None.
    """
    comments = ""
    docs = []
    error = None

    try:
        for n in node.children:
            if n.type == "comment":
                comments += n.text.decode("utf8") + "\n"
        if comments != "":
            logger.info(
                __name__,
                f"(extract_doc_csharp_one_func) comments retrieved from the function {funct_definition}: {comments}",
            )
            documentation, error = extract_doc_csharp(comments.replace("///", ""))

            if error is None:
                logger.info(
                    __name__,
                    f"(extract_doc_csharp_one_func) Successfully extracted the documentation for the function {funct_definition}",
                )
                docs.append(("subheader", f"Function: {funct_definition}"))
                docs.extend(documentation)
            else:
                logger.error(
                    __name__,
                    f"(extract_doc_csharp_one_func) Could't extract the documentation from the function {funct_definition}",
                )
                error = {
                    funct_definition: "Could't extract the documentation from the function."
                }
        else:
            # If comments weren't found
            logger.error(
                __name__,
                f"(extract_doc_csharp_one_func) Could't extract the comments from the function.",
            )
            error = {
                funct_definition: "Could't extract the comments from the function."
            }
    except Exception as e:
        logger.error(__name__, f"(extract_doc_csharp_one_func) {e}")

    return docs, error
