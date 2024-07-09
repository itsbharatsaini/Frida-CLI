import re
from tree_sitter import Tree, Language, Parser
import tree_sitter_c_sharp as tscsharp
from fridacli.frida_coder.languague import BaseLanguage
from typing_extensions import override
from fridacli.logger import Logger

logger = Logger()


class CSharp(BaseLanguage):
    __PARAM = (
        r"^\s*<\s*param\s*name\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</param>\s*$"
    )
    __RETURN = r"^\s*<\s*returns\s*>([\w\.\-\s<>=\"/{}]*)</returns>\s*$"
    __EXCEPTION = r"^\s*<\s*exception\s*cref\s*=\s*\"([\w\s.]*)\">([\w\.\-\s<>=\"/{}]*)</exception>\s*$"
    __PARSER = Parser(Language(tscsharp.language()))
    __COMMENT = "///"
    __NAME = "C#"

    def __init__(self) -> None:
        super().__init__()

    @property
    def parser(self):
        return self.__PARSER

    @property
    def comment(self):
        return self.__COMMENT

    @property
    def name(self):
        return self.__NAME

    # Methods for code execution
    @override
    def run(self, code: str):
        pass

    # Methods for code manipulation (static)
    @override
    def find_all_functions(self, code: str):
        """
        Finds and returns all the functions defined in the given code string.

        Args:
            code (str): The code string to search for functions.
        """
        try:
            tree = self.parser.parse(bytes(code, encoding="utf8"))
            return self.__help_find_all_functions(tree.root_node)
        except Exception as e:
            logger.error(__name__, f"(find_all_functions) {e}")
            return [], []

    def __help_find_all_functions(self, node: Tree):
        """
        Recursively finds all function and class definitions in a C# code tree.

        Args:
            node (Tree): The root node of the C# code tree.

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
                    f, c = self.__help_find_all_functions(n)
                    if f != []:
                        functions.extend(f)
                    if c != []:
                        classes.extend(c)
        except Exception as e:
            # If something went wrong, only empty lists are returned
            logger.error(__name__, f"(__help_find_all_functions) {e}")
            return [], []
        else:
            return functions, classes

    @override
    def extract_documentation(self, comments: str):
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

            params, returns, exceptions = [], [], []
            for comment in comments.splitlines():
                # Check if the current string refers to description, arguments, return values or exception
                param_match = re.match(
                    self.__PARAM,
                    comment,
                )
                returns_match = re.match(
                    self.__RETURN,
                    comment,
                )
                exception_match = re.match(
                    self.__EXCEPTION,
                    comment,
                )

                if param_match:
                    if first_parameter:
                        first_parameter = False
                    params.append(f"{param_match.group(1)}. {param_match.group(2)}")
                elif returns_match:
                    if first_return:
                        first_return = False
                    returns.append(f"{returns_match.group(1)}")
                elif exception_match:
                    if first_exception:
                        first_exception = False
                    exceptions.append(
                        f"{exception_match.group(1)}. {exception_match.group(2)}"
                    )
            if not first_parameter:
                lines.append(("bold", "Arguments:"))
                lines.append(("bullet_list", params))
            if not first_return:
                lines.append(("bold", "Return:"))
                lines.append(("bullet_list", returns))
            if not first_exception:
                lines.append(("bold", "Exceptions:"))
                lines.append(("bullet_list", exceptions))
        except Exception as e:
            logger.error(__name__, f"(extract_documentation) {e}")
            # If somethin went wrong, an empty list and the error is returned
            return [], e
        else:
            # If everything went right, the documentation and no errors are returned
            return lines, None

    @override
    def extract_doc_all_functions(self, code: str):
        """
        Extracts documentation from all functions in a C# abstract syntax tree.

        Args:
            code (str): The C# code.

        Returns:
            tuple: A tuple consisting of two lists. The first list contains the extracted documentation, organized as a list of tuples.
                The second list contains any encountered errors while extracting the documentation from the functions.
        """
        docs, errors = [], {}

        node = self.parser.parse(bytes(code, encoding="utf8"))
        functions, classes = self.find_all_functions(node)
        total = len(functions)
        documented = 0

        for func in functions:
            funct_definition = func["definition"]
            comments = func["comments"]
            if comments != "":
                logger.info(
                    __name__,
                    f"(extract_doc_all_functions) comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace("///", "")
                )
                if error is None:
                    logger.info(
                        __name__,
                        f"(extract_doc_all_functions) Successfully extracted the documentation for the function {funct_definition}",
                    )
                    docs.append(("subheader", f"Function: {funct_definition}"))
                    docs.extend(documentation)
                    documented += 1
                else:
                    # If something went wrong while extracting the documentation from the comments
                    logger.error(
                        __name__,
                        f"(extract_doc_all_functions) Could't extract the documentation from the function {funct_definition}",
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
                    f"(extract_doc_all_functions) Could't extract the comments from the function {funct_definition}.",
                )
                errors.update(
                    {
                        funct_definition: "Could't extract the comments from the function."
                    }
                )
        return docs, errors, (total, documented)

    @override
    def extract_doc_single_function(self, code: str, funct_definition: str):
        """
        Extracts the documentation from a C# function.

        Args:
            code (str): The C# function.
            funct_definition (str): The definition (name, args, return values) of the C# function.

        Returns:
            tuple: A list containing the extracted documentation as tuples.
                A dictionary containing the error message if a problem occurred during extraction, otherwise None.
        """
        comments = ""
        docs = []
        error = None

        node = self.parser.parse(bytes(code, encoding="utf8"))
        try:
            for n in node.children:
                if n.type == "comment":
                    comments += n.text.decode("utf8") + "\n"
            if comments != "":
                logger.info(
                    __name__,
                    f"(extract_doc_single_function) comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace("///", "")
                )

                if error is None:
                    logger.info(
                        __name__,
                        f"(extract_doc_single_function) Successfully extracted the documentation for the function {funct_definition}",
                    )
                    docs.append(("subheader", f"Function: {funct_definition}"))
                    docs.extend(documentation)
                else:
                    logger.error(
                        __name__,
                        f"(extract_doc_single_function) Could't extract the documentation from the function {funct_definition}",
                    )
                    error = {
                        funct_definition: "Could't extract the documentation from the function."
                    }
            else:
                # If comments weren't found
                logger.error(
                    __name__,
                    f"(extract_doc_single_function) Could't extract the comments from the function.",
                )
                error = {
                    funct_definition: "Could't extract the comments from the function."
                }
        except Exception as e:
            logger.error(__name__, f"(extract_doc_single_function) {e}")

        return docs, error
