import re
import os
import threading
from docx import Document
from mdutils.mdutils import MdUtils
from fridacli.logger import Logger
from fridacli.frida_coder import FridaCoder
from fridacli.file_manager import FileManager
from .predefined_phrases import (
    generate_document_for_funct_prompt,
    generate_full_document_prompt,
)
from .documentation import (
    extract_documentation_python,
    extract_functions_python,
    find_csharp_all_func,
    extract_doc_csharp_one_func,
    extract_doc_csharp_all_func,
)
from .regex_configuration import CODE_FROM_ALL_EXTENSIONS
import tree_sitter_c_sharp as tscsharp
from tree_sitter import Language, Parser

CS_LANGUAGE = Language(tscsharp.language())
parser = Parser(CS_LANGUAGE)

logger = Logger()

MAX_RETRIES = 2
SUPPORTED_DOC_EXTENSION = [".py", ".cs"]
COMMENT_CHARS = {
    ".py": '"""',
    ".cs": "///",
    ".java": "*",
    ".js": "*",
}


def save_documentation(path, lines):
    if "docx" in path:
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

        logger.info(__name__, f"Creating docx file in... {path}")
        doc.save(path)
    else:
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

        logger.info(__name__, f"Creating md file in... {path}")
        mdFile.create_md_file()


def extract_documentation(information, extension, one_function, funct_name):
    if extension == ".py":
        return extract_documentation_python(information, one_function, funct_name)
    elif extension == ".cs":
        tree = parser.parse(bytes(information["code"], encoding="utf8"))
        return (
            extract_doc_csharp_one_func(tree.root_node, funct_name)
            if one_function
            else extract_doc_csharp_all_func(tree.root_node)
        )
    else:
        logger.info(__name__, f"Do not support {extension} extension by now.")


def get_code_block(text, extension, one_function, funct_name=None):
    try:
        code_pattern = re.compile(CODE_FROM_ALL_EXTENSIONS, re.DOTALL)
        matches = code_pattern.findall(text)

        if matches == []:
            logger.info(__name__, f"Did not match: {text}")
        else:
            information = {"code": matches[0]}

            if extension in SUPPORTED_DOC_EXTENSION:
                lines = extract_documentation(
                    information, extension, one_function, funct_name
                )
                if lines is not None and lines != []:
                    information["documentation"] = lines
                    logger.info(__name__, f"Lines on doc: {lines}")
                else:
                    logger.info(
                        __name__,
                        f"Could not generate documentation for function {funct_name}",
                    )
            return information
    except Exception as e:
        logger.error(__name__, f"Error get code block from text using regex: {e}")


def write_code_to_path(path: str, code: str, extension: str, use_formatter: bool):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        if use_formatter:
            if extension == ".py":
                os.system(f"python -m black {path} -q")

    except Exception as e:
        pass
        # logger.error(__name__, f"Error writing code to path: {e}")


def document_file(
    formats,
    method,
    doc_path,
    use_formatter,
    file,
    thread_semaphore,
    chatbot_agent,
    file_manager: FileManager,
    frida_coder: FridaCoder,
):
    thread_semaphore.acquire()
    try:
        _, extension = os.path.splitext(file)
        if frida_coder.is_programming_language_extension(extension):
            logger.info(__name__, f"working on {file}")

            full_path = file_manager.get_file_path(file)

            code = frida_coder.get_code_from_path(full_path)
            num_lines = code.count("\n")

            new_file = []
            new_doc = [("title", f"Documentation of the file '{file}'")]
            new_code = None

            i = 1

            if extension not in SUPPORTED_DOC_EXTENSION:
                logger.info(
                    __name__,
                    f"Could not document {file} because {extension} is not supported.",
                )
            elif (
                method == "Slow"
                or num_lines <= 300
                or extension not in SUPPORTED_DOC_EXTENSION
            ):
                prompt = generate_full_document_prompt(code, extension)
                response = chatbot_agent.chat(prompt, True)

                while (
                    "```" not in response or COMMENT_CHARS[extension] not in response
                ) and i <= MAX_RETRIES:
                    logger.info(__name__, f"Retry # {i} for file {file}")
                    response = chatbot_agent.chat(prompt, True)
                    i += 1
                logger.info(__name__, f"file {file}, resp: {response}")
                if "```" in response and COMMENT_CHARS[extension] in response:
                    information = get_code_block(response, extension, False)
                    if information:
                        new_code = information["code"]
                        if "documentation" in information.keys():
                            new_doc.extend(information["documentation"])
                    else:
                        new_file = code.splitlines()
                else:
                    logger.info(__name__, f"Check response: {response}")
                    new_file = code.splitlines()

            else:
                tree = parser.parse(bytes(code, encoding="utf8"))

                functions, classes = find_csharp_all_func(tree.root_node)

                start_line = functions[0]["range"][0]
                end_line = functions[-1]["range"][-1]

                new_file.append(code[0 : start_line - 1])

                for func in functions:
                    funct_name = func["name"]
                    if func["comments"] == "":
                        prompt = generate_document_for_funct_prompt(
                            func["definition"] + func["body"], extension
                        )
                        response = chatbot_agent.chat(prompt, True)

                        while (
                            "```" not in response
                            or COMMENT_CHARS[extension] not in response
                        ) and i <= MAX_RETRIES:
                            logger.info(
                                __name__,
                                f"Retry # {i} for file {file} function {funct_name}",
                            )
                            response = chatbot_agent.chat(prompt, True)
                            i += 1
                        logger.info(__name__, f"Response: {response}")

                        if "```" in response and COMMENT_CHARS[extension] in response:
                            information = get_code_block(
                                response, extension, True, funct_name
                            )
                            if information:
                                document_code = information["code"]
                                document_code = ("\n" + document_code).splitlines()
                                new_file.extend(document_code)
                                if "documentation" in information.keys():
                                    new_doc.extend(information["documentation"])
                            else:
                                code = ("\n" + func["code"]).splitlines()
                                new_file.extend(code)
                        else:
                            logger.info(__name__, f"Check response: {response}")
                            code = ("\n" + func["code"]).splitlines()
                            new_file.extend(code)
                    else:
                        logger.info(
                            __name__, f"function already commented: {funct_name}"
                        )
                        code = (
                            "\n"
                            + func["comments"]
                            + "\n"
                            + func["definition"]
                            + func["body"]
                        ).splitlines()
                        new_file.extend(code)

                new_file.extend(code[end_line::])
                new_code = "\n".join(new_file)

        if new_code is not None:
            write_code_to_path(full_path, new_code, extension, use_formatter)
        else:
            logger.info(__name__, f"Could not write new code for file {file}")

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
            logger.info(__name__, f"Could not write new documentation for file {file}")
    except Exception as e:
        logger.info(__name__, f"Error in file: {file}: {e}")
    finally:
        thread_semaphore.release()


async def exec_document(
    formats,
    method,
    doc_path,
    use_formatter,
    chatbot_agent,
    file_manager: FileManager,
    frida_coder: FridaCoder,
):
    """
    Documenting all the files using threads
    """
    logger.info(__name__, f"Documenting files {method}")
    file_manager.load_folder(file_manager.get_folder_path())

    if method == "Slow":
        chatbot_agent.change_version(4)

    files = file_manager.get_files()
    thread_semaphore = threading.Semaphore(5)

    threads = []
    logger.info(__name__, f"size: {len(files)}")
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

    for thread in threads:
        thread.join()

    if method == "Slow":
        chatbot_agent.change_version(3)
