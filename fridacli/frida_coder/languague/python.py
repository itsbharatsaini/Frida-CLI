import os
import subprocess
from tree_sitter import Tree, Language, Parser
import tree_sitter_python as tspython
from fridacli.frida_coder.languague import BaseLanguage
from typing_extensions import override
from ..exception_message import ExceptionMessage
from fridacli.config import get_config_vars
from fridacli.logger import Logger

logger = Logger()


class Python(BaseLanguage):
    __PARSER = Parser(Language(tspython.language()))
    __COMMENT = '"""'
    __NAME = "Python"

    def __init__(self) -> None:
        super().__init__()
        self.__get_env()

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
    def run(self, path: None, file_extesion: str = None, file_exist: bool = False):
        """
        Run the code in the given path.
        TODO:
            Change for all the code runs using file exisiting why aviod using python eval
        """

        logger.info(
            __name__,
            f"(run) Running code in path: {path} with file extension: {str(file_extesion)} and file exist: {str(file_exist)}",
        )
        preprocessed_code = ""
        result_path = f"{self.result_files_dir}/{path}.txt"
        code_path = f"{self.code_files_dir}/{path}.{file_extesion}"

        if file_exist:
            directory, old_filename = os.path.split(path)
            file_name, file_extension = os.path.splitext(old_filename)
            result_path = f"{self.result_files_dir}/{file_name}_tmp.txt"
            code_path = path

        logger.info(
            __name__,
            f"(run) result path: {str(result_path)} code path: {str(code_path)}",
        )
        result_status = None
        try:
            with open(code_path, encoding="utf-8") as fl:
                code = fl.read()
                os.makedirs(os.path.dirname(result_path), exist_ok=True)
                preprocessed_code = code
                if file_exist:
                    result_status = self.__execute_existing_code(code_path, result_path)
                else:
                    preprocessed_code = self.__preprocess_code(code, result_path)
                    logger.info(__name__, f"preprocessed_code {preprocessed_code}")
                    result_status = self.__execute_code(preprocessed_code)
            return self.__build_result(result_path, result_status)
        except Exception as e:
            logger.error(__name__, f"Error running: {e}")

    def __get_env(self):
        """
        Get the python enviroment path
        """
        logger.info(__name__, "(get_env) Getting enviroment path")
        try:
            env_vars = get_config_vars()
            if "PYTHON_ENV_PATH" in env_vars:
                self.__PYTHON_ENV_PATH = env_vars["PYTHON_ENV_PATH"]
            else:
                self.__PYTHON_ENV_PATH = ""
        except Exception as e:
            logger.error(__name__, f"Error getting enviroment path: {e}")

    def __build_result(self, result_path, result_status):
        """
        Build the result of the execution
        """
        logger.info(
            __name__,
            f"(build_result) Building result with result path: {result_path} and result status: {result_status}",
        )
        if result_status == ExceptionMessage.EXEC_ERROR:
            return (result_status, None)
        result = self.__get_execution_result(result_path)
        if result == None:
            return (ExceptionMessage.GET_RESULT_ERROR, None)
        return (ExceptionMessage.GET_RESULT_SUCCESS, result)

    def __execute_code(self, code: str):
        try:
            """
            [Deplicated]
            TODO:
                When a funtion is exectuted and the is used in different blocks it can be used the problem
                is that for diferent prompts shouldn't have the same funtion

                Insted of globals() use another namespace to not compromise the exactution in runtime
            """

            exec(code, globals())
            return ExceptionMessage.EXEC_SUCCESS
        except:
            return ExceptionMessage.EXEC_ERROR

    def __execute_existing_code(self, code_path: str, result_path):
        """
        Execute the code that already exists in the file
        """
        logger.info(
            __name__,
            f"(execute_existing_code) Executing existing code in path: {str(code_path)} and result path: {str(result_path)}",
        )
        if len(self.__PYTHON_ENV_PATH) == 0:
            with open(result_path, "w") as f:
                f.write("No env configured")
            return ExceptionMessage.EXEC_SUCCESS

        try:
            """
            TODO:
                and also python3 or a posibility to change the variable name
            """
            result = subprocess.run(
                [self.__PYTHON_ENV_PATH, code_path], capture_output=True, text=True
            )
            logger.info(
                __name__, f"(execute_existing_code) Result: {str(result.stdout)}"
            )
            with open(result_path, "w") as f:
                f.write(result.stdout)
            return ExceptionMessage.EXEC_SUCCESS
        except:
            return ExceptionMessage.EXEC_ERROR

    def __get_execution_result(self, file_name):
        """
        Get the result of the execution
        """
        logger.info(
            __name__,
            f"(__get_execution_result) Getting execution result in file name: {file_name}",
        )
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                result = f.read()
                return result
        except Exception as e:
            logger.error(
                __name__,
                f"(__get_execution_result) Error getting execution result: {e}",
            )
            return None

    def __preprocess_code(self, code, path):
        """
        Preprocess the code to be executed
        """
        logger.info(__name__, f"(__preprocess_code) Preprocessing code")
        return self.__use_template(code, path)

    def __use_template(self, code, file_name):
        """
        Use the template to preprocess the code
        """
        logger.info(__name__, f"(__use_template) Using template")
        try:
            code_lines = code.split("\n")
            code_lines = [f"            {c}" for c in code_lines]
            code = "\n".join(code_lines)
            code = f"""
from contextlib import redirect_stdout
import traceback
with open(r'{file_name}', 'w', encoding='utf-8') as file:
    with redirect_stdout(file):
        try:
{code}
        except Exception as e:
            traceback_str = traceback.format_exc()
            file.write('ERROR\\n')
            file.write(traceback_str)
                
            """
            code_lines = code.split("\n")
            code_lines = [c for c in code_lines if c.strip() != ""]
            code = "\n".join(code_lines)
            logger.info(__name__, f"(__use_template) Code: {code}")
            return code
        except Exception as e:
            logger.error(__name__, f"Error using template: {e}")

    # Methods for code manipulation (static)
    @override
    def has_error(self, code):
        pass
    
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
        Recursively finds all function and class definitions in a Python code tree.

        Args:
            node (Tree): The root node of the Python code tree.

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
                    f, c = self.__help_find_all_functions(n)
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
                        args = []
                        for arg in sep[1:]:
                            if "None" not in arg and arg.strip() != "":
                                if first_parameter:
                                    lines.append(("bold", "Arguments:"))
                                    first_parameter = False
                                if ":" in arg:
                                    sep_arg = arg.strip().split(":", 1)
                                    if sep_arg[1] != "" and "-" not in sep_arg[0]:
                                        args.append(f"{sep_arg[0]}. {sep_arg[1]}")
                                    else:
                                        sep_arg = arg.strip()
                                        args[-1] = args[-1] + "\n" + arg.strip()
                                else:
                                    sep_arg = arg.strip()
                                    args[-1] = args[-1] + "\n" + arg.strip()
                        lines.append(("bullet_list", args))
                    elif "Returns:" in sep[0]:
                        # If Returns: in line, save all the return lines listed
                        rets = []
                        for ret in sep[1:]:
                            if "None" not in ret and ret.strip() != "":
                                if first_return:
                                    lines.append(("bold", "Returns:"))
                                    first_return = False
                                if ":" in ret:
                                    sep_ret = ret.strip().split(":", 1)
                                    if sep_ret[1] != "" and "-" not in sep_ret[0]:
                                        rets.append(f"{sep_ret[0]}. {sep_ret[1]}")
                                    else:
                                        sep_ret = ret.strip()
                                        rets[-1] = rets[-1] + "\n" + ret.rstrip()
                                else:
                                    sep_ret = ret.strip()
                                    rets[-1] = rets[-1] + "\n" + ret.rstrip()
                        lines.append(("bullet_list", rets))
                    elif "Raises:" in sep[0]:
                        # If Raises: in line, save all the exception lines listed
                        rais = []
                        for rai in sep[1:]:
                            if "None" not in rai and rai.strip() != "":
                                if first_exception:
                                    lines.append(("bold", "Raises:"))
                                    first_exception = False
                                if ":" in rai:
                                    sep_rai = rai.strip().split(":", 1)
                                    if sep_rai[1] != "" and "-" not in sep_rai[0]:
                                        rais.append(f"{sep_rai[0]}. {sep_rai[1]}")
                                    else:
                                        sep_rai = rai.strip()
                                        rais[-1] = rais[-1] + "\n" + rai.rstrip()
                                else:
                                    sep_rai = rai.strip()
                                    rais[-1] = rais[-1] + "\n" + rai.rstrip()
                        lines.append(("bullet_list", rais))
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
            logger.error(__name__, f"(extract_documentation) {e}")
            # If somethin went wrong, an empty list and the error is returned
            return [], e
        else:
            # If everything went right, the documentation and no errors are returned
            return lines, None

    @override
    def extract_doc_all_functions(self, code: str):
        """
        Extracts documentation from all functions in a Python abstract syntax tree.

        Args:
            code (str): The Python code.

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
                    comments.replace('"""', "")
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
        Extracts the documentation from a Python function.

        Args:
            code (str): The Python function.
            funct_definition (str): The definition (name, args, return values) of the Python function.

        Returns:
            tuple: A list containing the extracted documentation as tuples.
                A dictionary containing the error message if a problem occurred during extraction, otherwise None.
        """
        docs = []
        comments = ""
        error = None

        node = self.parser.parse(bytes(code, encoding="utf8"))

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
                    f"(extract_doc_single_function) comments retrieved from the function {funct_definition}: {comments}",
                )
                documentation, error = self.extract_documentation(
                    comments.replace('"""', "")
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
