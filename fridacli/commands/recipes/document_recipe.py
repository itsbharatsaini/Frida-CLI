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
from .documentation import (
    find_all_func_java,
    extract_doc_java_one_func,
    extract_doc_java_all_func,
    find_all_func_python,
    extract_doc_python_one_func,
    extract_doc_python_all_func,
    find_all_func_csharp,
    extract_doc_csharp_one_func,
    extract_doc_csharp_all_func,
)
from .regex_configuration import CODE_FROM_ALL_EXTENSIONS
import tree_sitter_c_sharp as tscsharp
import tree_sitter_python as tspython
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

# Loading grammars
CS_LANGUAGE = Language(tscsharp.language())
PY_LANGUAGE = Language(tspython.language())
JAVA_LANGUAGE = Language(tsjava.language())

logger = Logger()

MAX_RETRIES = 2
# Programming languages that can be fully documented without major issues
SUPPORTED_DOC_EXTENSION = [".py", ".cs", ".java"]
# The dictionary is structured as follows:
# extension: [documentation symbols, function to extract all functions, language parser,
#             function to extract documentation from one function, function to extract documentation from all functions]
COMMENT_EXTENSION = {
    ".py": [
        '"""',
        find_all_func_python,
        Parser(PY_LANGUAGE),
        extract_doc_python_one_func,
        extract_doc_python_all_func,
    ],
    ".cs": [
        "///",
        find_all_func_csharp,
        Parser(CS_LANGUAGE),
        extract_doc_csharp_one_func,
        extract_doc_csharp_all_func,
    ],
    ".java": [
        "/**",
        find_all_func_java,
        Parser(JAVA_LANGUAGE),
        extract_doc_java_one_func,
        extract_doc_java_all_func,
    ],
    ".js": ["*", None, None, None, None],
}
RESUMES = []


def save_documentation(path: str, lines: List[Tuple[str, str]]) -> None:
    """
    Save the documentation in either .docx or .md format.

    Args:
        path (str): The path to save the document.
        lines (List[Tuple[str, str]]): A list of tuples containing the format and text of each line.

    Raises:
        Exception: If any error occurs during the saving process.
    """
    try:
        if "docx" in path:
            logger.info(__name__, f"Saving documentation (docx) in: {path}")
            doc = Document()

            for format, text in lines:
                if format == "title":
                    doc.add_heading(text)
                elif format == "subheader":
                    doc.add_heading(text, level=2)
                elif format == "bold":
                    p = doc.add_paragraph("")
                    p.add_run(text).bold = True
                elif format == "text":
                    doc.add_paragraph(text)
                elif format == "bullet":
                    doc.add_paragraph(text, style="List Bullet")

            doc.save(path)
        else:
            logger.info(__name__, f"Saving documentation (md): {path}")
            mdFile = None
            bullets = []
            for format, text in lines:
                if format == "title":
                    mdFile = MdUtils(file_name=path)
                    mdFile.new_header(level=1, title=text, add_table_of_contents="n")
                elif format == "subheader":
                    if bullets:
                        mdFile.new_list(bullets)
                        bullets = []
                    mdFile.new_header(level=2, title=text, add_table_of_contents="n")
                elif format == "bold":
                    if bullets:
                        mdFile.new_list(bullets)
                        bullets = []
                    mdFile.new_line(text, bold_italics_code="b")
                elif format == "text":
                    mdFile.new_line(text)
                elif format == "bullet":
                    bullets.append(text)
            if bullets:
                mdFile.new_list(bullets)
                bullets = []

            mdFile.create_md_file()
        logger.info(__name__, f"Documentation saved succesfully.")
    except Exception as e:
        logger.error(__name__, f"(save_documentation) {e}")


def extract_documentation(
    code: str, extension: str, one_function: bool, funct_name: str | None
):
    """
    Extracts documentation from a provided code snippet (whole code or one function) based on the given file extension.

    Args:
        code (str): The actual code as a string.
        extension (str): The file extension of the code snippet.
        one_function (bool): Flag indicating whether to extract documentation for a single function or for the whole code snippet.
        funct_name (str, optional): The name of the function to extract documentation for if one_function is True.

    Returns:
        List[Tuple[str, str]] | None: The extracted documentation for the specified function or for the whole code snippet, if generated.
        List[Dict[str, str]] | str | None: Error(s) that might have happened.

    Raises:
        Exception: If there is an error during the extraction process.
    """
    try:
        if extension in SUPPORTED_DOC_EXTENSION:
            tree = COMMENT_EXTENSION[extension][2].parse(bytes(code, encoding="utf8"))
            return (
                COMMENT_EXTENSION[extension][3](tree.root_node, funct_name)
                if one_function
                else COMMENT_EXTENSION[extension][4](tree.root_node)
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
    funct_name: str | None = None,
):
    """
    Extracts the code block and documentation from the response.

    Args:
        text (str): The text containing code and maybe documentation.
        extension (str): The file extension of the code being extracted.
        one_function (bool): Whether to extract the documentation for one function or the whole code.
        funct_name (str, optional): The name of the specific function to extract code for. Defaults to None.

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
                        funct_name: "Couldn't generate the documentation for the function."
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
                        information["code"], extension, one_function, funct_name
                    )
                    count = None
                else:
                    lines, errors, count = extract_documentation(
                        information["code"], extension, one_function, funct_name
                    )

                # If documentation was returned
                if lines != []:
                    information["documentation"] = lines
                else:
                    logger.error(
                        __name__,
                        (
                            f"(get_code_block) Couldn't generate documentation for function {funct_name}"
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
                return information, (
                    {
                        funct_name: f"Couldn't extract the documentation to generate file because the {extension} extension is not supported."
                    }
                    if one_function
                    else f"Couldn't extract the documentation to generate file because the {extension} extension is not supported."
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
            all_errors = []

            i = 1

            if (
                method == "Slow"
                or num_lines <= 300
                or extension not in SUPPORTED_DOC_EXTENSION
            ):
                prompt = generate_full_document_prompt(code, extension)
                response = chatbot_agent.chat(prompt, True)

                while (
                    COMMENT_EXTENSION[extension][0] not in response
                ) and i <= MAX_RETRIES:
                    logger.info(
                        __name__,
                        f"(document_file) Retry # {i} for file {file}: {response}",
                    )
                    response = chatbot_agent.chat(prompt, True)
                    i += 1
                if COMMENT_EXTENSION[extension][0] in response:
                    logger.info(
                        __name__,
                        f"(document_file) Final response for the file {file}: {response}",
                    )
                    information, errors, count = get_code_block(
                        file, response, extension, False
                    )
                    if information is not None:
                        new_code = information["code"]
                        all_errors = errors
                        if "documentation" in information.keys():
                            new_doc.extend(information["documentation"])
                        if count is None:
                            tree = COMMENT_EXTENSION[extension][2].parse(
                                bytes(code, encoding="utf8")
                            )
                            functions, classes = COMMENT_EXTENSION[extension][1](
                                tree.root_node
                            )
                            total = len(functions)
                        else:
                            total, documented = count
                    else:
                        global_error = errors
                else:
                    logger.info(
                        __name__,
                        f"(document_file) Couldn't get the expected response for the file {file}: {response}",
                    )
                    global_error = "Couldn't generate the documentation for the file."
                    functions, classes = COMMENT_EXTENSION[extension][1](tree.root_node)
                    total = len(functions)

                RESUMES.append(
                    {
                        "file": file,
                        "global_error": global_error,
                        "total_functions": total,
                        "documented_functions": documented,
                        "function_errors": all_errors,
                    }
                )

            else:
                tree = COMMENT_EXTENSION[extension][2].parse(
                    bytes(code, encoding="utf8")
                )

                functions, classes = COMMENT_EXTENSION[extension][1](tree.root_node)
                total = len(functions)
                documented = 0
                all_errors = []

                start_line = functions[0]["range"][0]
                end_line = functions[-1]["range"][-1]

                new_file.append(code[: start_line - 1])
                for func in functions:
                    funct_name = func["name"]
                    func_body = func["definition"] + "\n" + func["body"]
                    logger.info(
                        __name__,
                        f"(document_file) Code for the function {funct_name}: {func_body}",
                    )
                    prompt = generate_document_for_funct_prompt(
                        func["definition"] + func["body"], extension
                    )
                    response = chatbot_agent.chat(prompt, True)

                    while (
                        COMMENT_EXTENSION[extension][0] not in response
                    ) and i <= MAX_RETRIES:
                        logger.info(
                            __name__,
                            f"(document_file) Retry # {i} for file {file} function {funct_name} response: {response}",
                        )
                        response = chatbot_agent.chat(prompt, True)
                        i += 1
                    i = 1

                    if COMMENT_EXTENSION[extension][0] in response:
                        logger.info(
                            __name__,
                            f"(document_file) Final response for the function {funct_name}: {response}",
                        )
                        information, errors, _ = get_code_block(
                            file, response, extension, True, funct_name
                        )
                        if information is not None:
                            document_code = information["code"]
                            document_code = ("\n" + document_code).splitlines()
                            new_file.extend(document_code)
                            if "documentation" in information.keys():
                                new_doc.extend(information["documentation"])
                                documented += 1
                        if errors is not None:
                            all_errors.extend(errors)
                    else:
                        new_lines = (
                            "\n" + func["definition"] + func["body"]
                        ).splitlines()
                        new_file.extend(new_lines)
                        all_errors.append(
                            {
                                funct_name: "Couldn't generate the documentation for the function."
                            }
                        )

                new_file.extend(code[end_line:])
                new_code = "\n".join(new_file)

                RESUMES.append(
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
                        save_documentation(os.path.join(doc_path, filename), new_doc)
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

    return RESUMES
