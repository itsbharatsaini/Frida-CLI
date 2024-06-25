import re
import os
import threading
from typing import List, Tuple, Dict
from docx import Document
from mdutils.mdutils import MdUtils
from fridacli.logger import Logger
from fridacli.chatbot import ChatbotAgent
from fridacli.frida_coder import FridaCoder
from fridacli.file_manager import FileManager
from .predefined_phrases import (
    generate_document_for_funct_prompt,
    generate_full_document_prompt,
)
from .utils import create_file
from fridacli.frida_coder.languague.python import Python
from fridacli.frida_coder.languague.csharp import CSharp
from fridacli.frida_coder.languague.java import Java
from fridacli.logger import Logger

logger = Logger()

CODE_FROM_ALL_EXTENSIONS = r"```(?:javascript|java|csharp|c#|C#|python)*(.*)```"
MAX_RETRIES = 2
# Programming languages that can be fully documented without major issues
SUPPORTED_DOC_EXTENSION = [".py", ".cs", ".java"]
# The dictionary is structured as follows:
# extension: [documentation symbols, function to extract all functions, language parser,
#             function to extract documentation from one function, function to extract documentation from all functions]
LANGUAGES = {
    ".py": Python(),
    ".cs": CSharp(),
    ".java": Java(),
    ".js": "*",
}
resumes = []

def extract_documentation(
    code: str,
    extension: str,
    one_function: bool,
    funct_definition: str | None,
):
    """
    Extracts documentation from a provided code snippet (whole code or one function) based on the given file extension.

    Args:
        code (str): The actual code as a string.
        extension (str): The file extension of the code snippet.
        one_function (bool): Flag indicating whether to extract documentation for a single function or for the whole code snippet.
        funct_definition (str, optional): The definition (name, args, return values) of the function to extract documentation for if one_function is True.

    Returns:
        List[Tuple[str, str]] | None: The extracted documentation for the specified function or for the whole code snippet, if generated.
        List[Dict[str, str]] | str | None: Error(s) that might have happened.

    Raises:
        Exception: If there is an error during the extraction process.
    """
    try:
        if extension in SUPPORTED_DOC_EXTENSION:
            tree = LANGUAGES[extension].parser.parse(bytes(code, encoding="utf8"))
            return (
                LANGUAGES[extension].extract_doc_single_function(tree.root_node, funct_definition)
                if one_function
                else LANGUAGES[extension].extract_doc_all_functions(tree.root_node)
            )
        else:
            logger.error(
                __name__,
                f"(extract_documentation) Do not support the {extension} extension by now.",
            )
    except Exception as e:
        logger.error(__name__, f"(extract_documentation) {e}")
        return [], e


def get_code_block(
    file_name: str,
    text: str,
    extension: str,
    one_function: bool,
    funct_definition: str | None = None,
):
    """
    Extracts the code block and documentation from the response.

    Args:
        text (str): The text containing code and maybe documentation.
        extension (str): The file extension of the code being extracted.
        one_function (bool): Whether to extract the documentation for one function or the whole code.
        funct_definition (str, optional): The definition (name, params, return values) of the specific function to extract code for. Defaults to None.

    Returns:
        Dict[str, str | List[Tuple[str, str]]]: A dictionary containing the extracted code and documentation, if applicable.
        List[Dict[str, str]] | str | None: Error(s) that might have happened.
        Tuple[int, int] | None: Number of functions in total and the number of functions documented, if applicable.

    Raises:
        Exception: If there is an error while executing the function.
    """
    try:
        # Extracts the code block from the response
        code_pattern = re.compile(CODE_FROM_ALL_EXTENSIONS, re.DOTALL)
        matches = code_pattern.findall(text)

        if matches == []:
            logger.error(
                __name__,
                f"(get_code_block) Didn't match to extract the code block: {text}",
            )
            return (
                None,
                (
                    {
                        funct_definition: "Couldn't generate the documentation for the function."
                    }
                    if one_function
                    else "Couldn't generate the documentation for the file."
                ),
                None,
            )
        else:
            information = {"code": matches[0].replace("```", "")}
            logger.info(
                __name__,
                f"(get_code_block) code block: {matches[0].replace('```', '')}",
            )

            if extension in SUPPORTED_DOC_EXTENSION:
                if one_function:
                    lines, errors = extract_documentation(
                        information["code"],
                        extension,
                        one_function,
                        funct_definition,
                    )
                    count = None
                else:
                    lines, errors, count = extract_documentation(
                        information["code"],
                        extension,
                        one_function,
                        funct_definition,
                    )

                # If documentation was returned
                if lines != []:
                    information["documentation"] = lines
                else:
                    logger.error(
                        __name__,
                        (
                            f"(get_code_block) Couldn't generate documentation for function {funct_definition}"
                            if one_function
                            else f"(get_code_block) Couldn't generate documentation for file {file_name}"
                        ),
                    )
                return information, errors, count
            else:
                logger.error(
                    __name__,
                    f"(get_code_block) Do not support the {extension} extension by now.",
                )
                return (
                    information,
                    (
                        {
                            funct_definition: f"Couldn't extract the documentation to generate file because the {extension} extension is not supported."
                        }
                        if one_function
                        else f"Couldn't extract the documentation to generate file because the {extension} extension is not supported."
                    ),
                    None,
                )
    except Exception as e:
        logger.error(__name__, f"(get_code_block) {e}")
        return None, e, None


def write_code_to_path(
    path: str, code: str, extension: str, use_formatter: bool
) -> None:
    """
    Writes code to a file located at the given path.

    Args:
        path (str): The path to the file.
        code (str): The code to be written to the file.
        extension (str): The file extension to determine the file type.
        use_formatter (bool): Flag to indicate whether to use a code formatter on the file.

    Raises:
        Exception: If an error occurs while writing the code to the file.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        if use_formatter:
            if extension == ".py":
                os.system(f"python -m black {path} -q")

    except Exception as e:
        logger.error(__name__, f"(write_code_to_path) {e}")


def document_file(
    formats: Dict[str, bool],
    method: str,
    doc_path: str,
    use_formatter: bool,
    file: str,
    thread_semaphore: threading.Semaphore,
    chatbot_agent: ChatbotAgent,
    file_manager: FileManager,
    frida_coder: FridaCoder,
) -> None:
    thread_semaphore.acquire()

    try:
        _, extension = os.path.splitext(file)
        if frida_coder.is_programming_language_extension(extension):
            logger.info(__name__, f"(document_file) Working on {file}")

            full_path = file_manager.get_file_path(file)

            code = frida_coder.get_code_from_path(full_path)
            num_lines = code.count("\n")

            new_file = []
            new_doc = [("title", f"Documentation of the file '{file}'")]
            new_code = None

            global_error = None
            total = 0
            documented = 0
            all_errors = {}

            i = 1

            if (
                method == "Slow"
                or num_lines <= 300
                or extension not in SUPPORTED_DOC_EXTENSION
            ):
                prompt = generate_full_document_prompt(code, extension)
                response = chatbot_agent.chat(prompt, True)
                comment = LANGUAGES[extension] if extension not in SUPPORTED_DOC_EXTENSION else LANGUAGES[extension].comment

                while (
                    comment not in response and "```" not in response
                ) and i <= MAX_RETRIES:
                    logger.info(
                        __name__,
                        f"(document_file) Retry # {i} for file {file}: {response}",
                    )
                    response = chatbot_agent.chat(prompt, True)
                    i += 1

                if comment in response and "```" in response:
                    logger.info(
                        __name__,
                        f"(document_file) Final response for the file {file}: {response}",
                    )
                    information, errors, count = get_code_block(
                        file, response, extension, False
                    )
                    if information is not None:
                        new_code = information["code"]
                        if extension in SUPPORTED_DOC_EXTENSION:
                            all_errors = errors
                        if "documentation" in information.keys():
                            new_doc.extend(information["documentation"])
                        if count is None and extension in SUPPORTED_DOC_EXTENSION:
                            tree = LANGUAGES[extension].parser.parse(
                                bytes(code, encoding="utf8")
                            )
                            functions, classes = LANGUAGES[extension].find_all_functions(tree.root_node)
                            total = len(functions)
                        elif extension in SUPPORTED_DOC_EXTENSION:
                            total, documented = count
                        else:
                            total = -1
                    else:
                        global_error = errors
                        if extension in SUPPORTED_DOC_EXTENSION:
                            tree = LANGUAGES[extension].parser.parse(
                                bytes(code, encoding="utf8")
                            )
                            functions, classes = LANGUAGES[extension].find_all_functions(tree.root_node)
                            total = len(functions)
                else:
                    logger.info(
                        __name__,
                        f"(document_file) Couldn't get the expected response for the file {file}: {response}",
                    )
                    global_error = "Couldn't generate the documentation for the file."
                    if extension in SUPPORTED_DOC_EXTENSION:
                        tree = LANGUAGES[extension].parser.parse(
                            bytes(code, encoding="utf8")
                        )
                        functions, classes = LANGUAGES[extension].find_all_functions(tree.root_node)
                        total = len(functions)

                resumes.append(
                    {
                        "file": file,
                        "global_error": global_error,
                        "total_functions": total,
                        "documented_functions": documented,
                        "function_errors": all_errors,
                    }
                )

            else:
                tree = LANGUAGES[extension].parser.parse(
                    bytes(code, encoding="utf8")
                )

                functions, classes = LANGUAGES[extension].find_all_functions(tree.root_node)
                total = len(functions)
                documented = 0
                all_errors = {}

                start_line = functions[0]["range"][0]
                end_line = functions[-1]["range"][-1]

                new_file.append(code[: start_line - 1])
                for func in functions:
                    funct_definition = func["definition"]
                    funct_body = func["definition"] + "\n" + func["body"]
                    logger.info(
                        __name__,
                        f"(document_file) Code for the function {funct_definition}: {funct_body}",
                    )
                    prompt = generate_document_for_funct_prompt(
                        funct_body, extension
                    )
                    response = chatbot_agent.chat(prompt, True)

                    while (
                        LANGUAGES[extension].comment not in response
                        and "```" not in response
                    ) and i <= MAX_RETRIES:
                        logger.info(
                            __name__,
                            f"(document_file) Retry # {i} for file {file} function {funct_definition} response: {response}",
                        )
                        response = chatbot_agent.chat(prompt, True)
                        i += 1
                    i = 1

                    if (
                        LANGUAGES[extension].comment in response
                        and "```" in response
                    ):
                        logger.info(
                            __name__,
                            f"(document_file) Final response for the function {funct_definition}: {response}",
                        )
                        information, errors, _ = get_code_block(
                            file, response, extension, True, funct_definition
                        )
                        if information is not None:
                            document_code = information["code"]
                            document_code = ("\n" + document_code).splitlines()
                            new_file.extend(document_code)
                            if "documentation" in information.keys():
                                new_doc.extend(information["documentation"])
                                documented += 1
                        if errors is not None:
                            all_errors.update(errors)
                    else:
                        new_lines = (
                            "\n" + func["definition"] + func["body"]
                        ).splitlines()
                        new_file.extend(new_lines)
                        all_errors.update(
                            {
                                funct_definition: "Couldn't generate the documentation for the function."
                            }
                        )

                new_file.extend(code[end_line:])
                new_code = "\n".join(new_file)

                resumes.append(
                    {
                        "file": file,
                        "global_error": None,
                        "total_functions": total,
                        "documented_functions": documented,
                        "function_errors": all_errors,
                    }
                )

            # If there is new code to write
            if new_code is not None:
                logger.info(
                    __name__,
                    f"(document_file) Writing the documented code for the file {file}",
                )
                write_code_to_path(full_path, new_code, extension, use_formatter)
            else:
                logger.error(
                    __name__,
                    f"(document_file) Could not write new code for file {file}",
                )

            # If there is at least one new line of documentation
            if len(new_doc) > 1:
                for doctype, selected in formats.items():
                    if selected:
                        filename = (
                            ("readme_" + file + ".md")
                            if doctype == "md"
                            else ("doc_" + file + ".docx")
                        )
                        create_file(os.path.join(doc_path, filename), new_doc)
            else:
                logger.error(
                    __name__,
                    f"(document_file) Could not write new documentation for file {file}",
                )
    except Exception as e:
        logger.error(__name__, f"(document_file) {e}")
    finally:
        thread_semaphore.release()


async def exec_document(
    formats: Dict[str, bool],
    method: str,
    doc_path: str,
    use_formatter: bool,
    chatbot_agent: ChatbotAgent,
    file_manager: FileManager,
    frida_coder: FridaCoder,
):
    """
    Execute the document generation process for multiple files.

    Args:
        formats (Dict[str, bool]): A dictionary of file formats and their corresponding boolean values indicating whether
            to generate documents in that format.
        method (str): The method used for document generation.
        doc_path (str): The path where the generated documents will be saved.
        use_formatter (bool): A boolean indicating whether to use a formatter during the document generation process.
        chatbot_agent (ChatbotAgent): The chatbot agent object that will be used during the document generation process.
        file_manager (FileManager): The file manager object responsible for loading and managing files.
        frida_coder (FridaCoder): The Frida coder object that will be used for code-related methods.
    """
    # Loading current directory
    file_manager.load_folder(file_manager.get_folder_path())

    # If the method is slow, the chat is changed to ChatGPT-4
    if method == "Slow":
        chatbot_agent.change_version(4)

    files = file_manager.get_files()
    threads = []
    thread_semaphore = threading.Semaphore(5)
    logger.info(
        __name__,
        f"(exec_document) Documenting {len(files)} files using the method {method}",
    )

    for file in files:
        thread = threading.Thread(
            target=document_file,
            args=(
                formats,
                method,
                doc_path,
                use_formatter,
                file,
                thread_semaphore,
                chatbot_agent,
                file_manager,
                frida_coder,
            ),
        )
        threads.append(thread)
        thread.start()

    # Joining all the threads
    for thread in threads:
        thread.join()

    # If the method is slow, the chat is changed back ChatGPT-3.x
    if method == "Slow":
        chatbot_agent.change_version(3)

    logger.info(__name__, f"(exec_document) The final resumes: {resumes}")

    # The resumes variable is cleaned
    temp = resumes.copy()
    resumes.clear()

    return temp
