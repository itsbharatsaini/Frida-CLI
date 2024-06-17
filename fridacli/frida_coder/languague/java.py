import re
from tree_sitter import Tree, Language, Parser
import tree_sitter_java as tsjava
from fridacli.frida_coder.languague import Language
from typing_extensions import override
from fridacli.logger import Logger

logger = Logger()


class Java(Language):
    __PARAM = r"\s*\*\s*@param\s*([\w_\d]*)\s*(.*)\s*"
    __RETURN = r"\s*\*\s*@return\s*(.*)\s*"
    __EXCEPTION = r"\s*\*\s*@throws\s*([\w_\d]*)\s*(.*)\s*"
    __DESCRIPTION = r"\s*\*\s*(.*)\s*"
    __PARSER = Parser(Language(tsjava.language()))
    __COMMENT = "/**"

    def __init__(self) -> None:
        super().__init__()

    @property
    def parser(self):
        return self.__PARSER

    @property
    def comment(self):
        return self.__COMMENT

    # Methods for code execution
    @override
    def run(self, code: str):
        pass

    # Methods for code manipulation (static)
    @override
    def find_all_functions(self, node: Tree):
        """
        Recursively finds all function and class definitions in a Java code tree.

        Args:
            node (Tree): The root node of the Java code tree.

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
                    f, c = self.find_all_functions(n)
                    if f != []:
                        functions.extend(f)
                    if c != []:
                        classes.extend(c)
        except Exception as e:
            # If something went wrong, only empty lists are returned
            logger.error(__name__, f"(find_all_functions) {e}")
            return [], []
        else:
            return functions, classes

    @override
    def extract_documentation(self, comments: str):
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
                    description_match = re.match(self.__DESCRIPTION, line)
                    param_match = re.match(self.__PARAM, line)
                    returns_match = re.match(self.__RETURN, line)
                    exception_match = re.match(self.__EXCEPTION, line)

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
            logger.error(__name__, f"(extract_documentation) {e}")
            # If somethin went wrong, an empty list and the error is returned
            return [], e
        else:
            # If everything went right, the documentation and no errors are returned
            return lines, None

    @override
    def extract_doc_all_functions(self, node: Tree):
        """
        Extracts documentation from all functions in a Java abstract syntax tree.

        Args:
            node (Tree): The abstract syntax tree node representing the Java code.

        Returns:
            tuple: A tuple consisting of two lists. The first list contains the extracted documentation, organized as a list of tuples.
                The second list contains any encountered errors while extracting the documentation from the functions.
        """
        docs, errors = [], {}

        functions, classes = self.find_all_functions(node)
        total = len(functions)
        documented = 0

        for func in functions:
            funct_definition = func["definition"]
            comments = func["comments"]
            if comments != "":
                logger.info(
                    __name__,
                    f"(extract_doc_all_functions) Comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace("*/", "").replace("/**", "")
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
    def extract_doc_single_function(self, node: Tree, funct_definition: str):
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
                    f"(extract_doc_single_function) Comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace("*/", "").replace("/**", "")
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
                    f"(extract_doc_single_function) Could't extract the comments from the function {funct_definition}",
                )
                error = {
                    funct_definition: "Could't extract the comments from the function."
                }
        except Exception as e:
            logger.error(__name__, f"(extract_doc_single_function) {e}")

        return docs, error
