import re
from fridacli.frida_coder.languague import BaseLanguage
from typing_extensions import override
from fridacli.logger import Logger

logger = Logger()


class VisualBasic(BaseLanguage):
    __COMMENT = "'==============================================="
    __NAME = "Visual Basic"
    __FUNCTION = (
        r"((?:Public|Private)\s*Function\s*([\w_\d]*)\s*\((?:.*)\)\s*As\s*(?:[\w]*))"
    )
    __SUB = r"((?:Public|Private)\s*Sub\s*([\w_\d]*)\s*\((?:.*)\))"
    __RETURN = r"Returns:\s*([\w]*)\s*-\s*(.*)"
    __PARAM = r"\s*([\w]*)\s*-\s*(.*) \(([\w]*)\)"

    def __init__(self) -> None:
        super().__init__()

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
        functions = []
        comment = False
        start_comment = -1
        end_comment = -1
        comment_text = ""

        try:
            for line in code.splitlines():
                if comment and self.__COMMENT in line:
                    comment = False
                    comment_text += line + "\n"
                elif self.__COMMENT in line:
                    comment = True
                    comment_text += line + "\n"
                elif comment:
                    comment_text += line + "\n"

                matches = re.match(self.__FUNCTION, line)

                if matches:
                    start = code.find(matches.group(0))
                    definition = matches.group(1)
                    name = matches.group(2)
                    end = code.find("End Function\n", start)
                    body = code[start + len(definition) + 1 : end + 13]
                    if comment_text != "":
                        start_comment = code.find(comment_text)
                        end_comment = start_comment + len(comment_text)
                    functions.append(
                        {
                            "is_function": True,
                            "name": name,
                            "definition": definition,
                            "body": body,
                            "range": (start, end + 13),
                            "comments": comment_text,
                            "comments_range": (start_comment, end_comment),
                        }
                    )
                    comment_text = ""

                matches = re.match(self.__SUB, line)

                if matches:
                    start = code.find(matches.group(0))
                    definition = matches.group(1)
                    name = matches.group(2)
                    end = code.find("End Sub\n", start)
                    body = code[start + len(definition) + 1 : end + 8]
                    functions.append(
                        {
                            "is_function": False,
                            "name": name,
                            "definition": definition,
                            "body": body,
                            "range": (start, end + 8),
                            "comments": comment_text,
                            "comments_range": (start_comment, end_comment),
                        }
                    )
                    comment_text = ""
        except Exception as e:
            logger.error(__name__, f"(find_all_functions) {e}")
        finally:
            return functions, None

    def extract_documentation(self, comments: str, is_function: bool):
        """
        Extracts documentation from Python-style comments.

        Args:
            comments (str): The string containing the Python-style comments.
            is_function (bool): To distinguish between functions and subroutines.

        Returns:
            Tuple[List, str | None]: A tuple containing the extracted documentation as a list of formatted lines and an optional error message.
        """
        lines = []
        parameters = []
        read_param = False
        read_error = False

        try:
            if is_function:
                for line in comments.splitlines():
                    print(line)
                    if "Description:" in line:
                        description = ":".join(line.split(":")[1:]).strip()
                        print(description)
                        if description != "":
                            lines.append(("bold", "Description:"))
                            lines.append(("text", description))
                    elif "Returns: " in line:
                        read_param = False
                        if parameters != []:
                            lines.append(("bold", "Arguments:"))
                            lines.append(("bullet_list", parameters))
                        matches = re.match(self.__RETURN, line)
                        if matches:
                            lines.append(("bold", "Return:"))
                            lines.append(
                                ("text", f"({matches.group(1)}). {matches.group(2)}.")
                            )
                    elif "Parameters:" in line:
                        read_param = True
                    elif "Error Handling:" in line:
                        read_error = True
                    elif read_param:
                        matches = re.match(self.__PARAM, line)
                        if matches:
                            parameters.append(
                                f"{matches.group(1)} ({matches.group(3)}). {matches.group(2)}."
                            )
                    elif read_error:
                        if "None" not in line.strip() and line.strip() != "":
                            lines.append(("bold", "Error Handling:"))
                            lines.append(("text", line.strip()))
                        read_error = False
            else:
                for line in comments.splitlines():
                    print(line)
                    if "Description:" in line:
                        description = ":".join(line.split(":")[1:]).strip()
                        print(description)
                        if description != "":
                            lines.append(("bold", "Description:"))
                            lines.append(("text", description))
                    elif "Parameters:" in line:
                        read_param = True
                    elif "Error Handling:" in line:
                        read_error = True
                        read_param = False
                        if parameters != []:
                            lines.append(("bold", "Arguments:"))
                            lines.append(("bullet_list", parameters))
                    elif read_param:
                        matches = re.match(self.__PARAM, line)
                        if matches:
                            parameters.append(
                                f"{matches.group(1)} ({matches.group(3)}). {matches.group(2)}."
                            )
                    elif read_error:
                        if "None" not in line.strip() and line.strip() != "":
                            lines.append(("bold", "Error Handling:"))
                            lines.append(("text", line.strip()))
                        read_error = False
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
        Extracts documentation from all functions in a Python code.

        Args:
            code (str): The Python code.

        Returns:
            tuple: A tuple consisting of two lists. The first list contains the extracted documentation, organized as a list of tuples.
                The second list contains any encountered errors while extracting the documentation from the functions.
        """
        docs, errors = [], {}

        functions, classes = self.find_all_functions(code)
        total = len(functions)
        documented = 0

        for func in functions:
            funct_definition = func["definition"]
            comments = func["comments"]
            is_function = func["is_function"]
            if comments != "":
                logger.info(
                    __name__,
                    f"(extract_doc_all_functions) Comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace(self.__COMMENT, "").replace("'", ""), is_function
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

    def extract_doc_single_function(
        self, code: str, funct_definition: str, is_function: bool
    ):
        """
        Extracts the documentation from a Python function.

        Args:
            node (Tree): The tree representing the Python function.
            funct_definition (str): The definition (name, args, return value) of the Python function.
            is_function (bool): To distinguish between functions and subroutines.
            
        Returns:
            tuple: A list containing the extracted documentation as tuples.
                A dictionary containing the error message if a problem occurred during extraction, otherwise None.
        """
        comments = ""
        error = None
        docs = []

        try:
            start = code.find(self.__COMMENT)
            end = code.find(self.__COMMENT, start + 1)
            comments = code[start:end]

            if comments != "":
                logger.info(
                    __name__,
                    f"(extract_doc_single_function) Comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace(self.__COMMENT, "").replace("'", ""), is_function
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
