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
from .documentation import extract_documentation_python, extract_documentation_csharp

logger = Logger()

MAX_RETRIES = 2
EXTENSIONS = {
    ".py": [
        '"""',
        r"```(python)*\s*((?:[\w._,\s]*)*(?:\"\"\"\s*([\w.\-,\'_:=#\[\(\)\]\s]*)\"\"\"\s*)*.*)```",
        "",
        [r"^\s*def\s*([\w\d_]*)\s*\(\s*(?:[\w:\d_]*)\s*\)\s*:\s*$"],
    ],
    ".cs": [
        "///",
        r"```([\w#]*)\s*([\w.;\s]*\s*(?:///\s*<\s*summary\s*>\s*///\s*([\w.\-,:#\[()\]\d\s]*)///\s*<\s*/\s*summary\s*>)*\s*.*)```",
        "/",
    ],
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

        logger.info(__name__, f"Creating doc in... {path}")
        mdFile.create_md_file()


def extract_documentation(information, extension, one_function, funct_name):
    if extension == ".py":
        return extract_documentation_python(information, one_function, funct_name)
    elif extension == ".cs":
        return extract_documentation_csharp(information, one_function, funct_name)
    else:
        logger.info(__name__, f"Do not support {extension} extension by now.")


def get_code_block(text, extension, one_function, funct_name=None):
    try:
        code_pattern = re.compile(EXTENSIONS[extension][1], re.DOTALL)
        matches = code_pattern.findall(text)

        if matches == []:
            logger.info(__name__, f"Did not match: {text}")
        else:
            information = {
                "language": matches[0][0],
                "code": matches[0][1],
                "description": matches[0][2]
                .replace(EXTENSIONS[extension][2], "")
                .replace("`", ""),
            }

            logger.info(__name__, information)
            lines = extract_documentation(
                information, extension, one_function, funct_name
            )
            if lines is not None:
                information["documentation"] = lines
            return information
    except Exception as e:
        logger.error(__name__, f"Error get code block from text using regex: {e}")


def write_code_to_path(path: str, code: str):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        pass
        # logger.error(__name__, f"Error writing code to path: {e}")


def extract_functions(code):
    functions = []
    current_function = None
    current_function_lines = []
    brace_count = 0
    order = 0
    start_line = 0

    for idx, line in enumerate(code, 1):
        line = line.strip()

        # Check if it's a function definition
        function_match = re.match(
            r"^\s*(?:(?:public|private|protected|internal|static|async|unsafe|sealed|new|override|virtual|abstract)\s+)+([\w<>\[\],\.]+\s+)+([\w_]+)\s*\((.*)\)\s*(?:where.*)?\s*$",
            line,
        )
        if function_match:
            order += 1
            start_line = idx
            return_type = function_match.group(1)
            function_name = function_match.group(2)
            # logger.info(__name__, f"line: {idx} Return: {function_match.group(1)} Name: {function_match.group(2)} Args: {function_match.group(3)}")
            current_function = function_name
            current_function_lines = [line]
            brace_count = 1 if line.endswith("{") else 0
            continue

        # If inside a function, add lines to its list
        if current_function:
            current_function_lines.append(line)
            brace_count += line.count("{")
            brace_count -= line.count("}")

        # Check if the function ends
        if brace_count == 0 and current_function:
            functions.append(
                {
                    "order": order,
                    "start_line": start_line,
                    "end_line": idx,
                    "name_of_function": current_function,
                    "code": "\n".join(current_function_lines),
                }
            )
            current_function = None
            current_function_lines = []
    return functions


def document_file(
    formats,
    method,
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
            doc_path = "".join(full_path.split(file)[:-1])

            code = frida_coder.get_code_from_path(full_path)
            num_lines = code.count("\n")

            new_file = []
            new_doc = [("title", f"Documentation of the file '{file}'")]

            i = 1

            if method == "Quick":

                if num_lines <= 300:
                    logger.info(
                        __name__, f"{extension} {file} with {num_lines} lines... 1"
                    )
                    prompt = generate_full_document_prompt(code, extension)
                    logger.info(__name__, f"{file} with {num_lines} lines... 2")
                    response = chatbot_agent.chat(prompt, True)
                    logger.info(__name__, f"{file} with {num_lines} lines... 3")

                    while (
                        "```" not in response
                        or EXTENSIONS[extension][0] not in response
                    ) and i <= MAX_RETRIES:
                        logger.info(__name__, f"Retry # {i} for file {file}")
                        response = chatbot_agent.chat(prompt, True)
                        i += 1
                    logger.info(__name__, f"{file} with {num_lines} lines... 4")
                    logger.info(__name__, response)
                    if "```" in response and EXTENSIONS[extension][0] in response:
                        information = get_code_block(response, extension, False)
                        if information:
                            new_code = information["code"]
                            new_doc.extend(information["documentation"])
                        else:
                            new_file = code.splitlines()
                    else:
                        logger.info(__name__, f"Check response: {response}")
                        new_file = code.splitlines()

                else:
                    logger.info(__name__, f"Else... more than 300 lines")
                    code = code.splitlines()
                    functions = extract_functions(code)

                    start_line = functions[0]["start_line"]
                    end_line = functions[-1]["end_line"]

                    new_file.extend(code[0 : start_line - 1])

                    for func in functions:
                        funct_name = func["name_of_function"]
                        prompt = generate_document_for_funct_prompt(
                            func["code"], extension
                        )
                        response = chatbot_agent.chat(prompt, True)

                        while (
                            "```" not in response
                            or EXTENSIONS[extension][0] not in response
                        ) and i <= MAX_RETRIES:
                            logger.info(
                                __name__,
                                f"Retry # {i} for file {file} function {funct_name}",
                            )
                            response = chatbot_agent.chat(prompt, True)
                            i += 1

                        if "```" in response and EXTENSIONS[extension][0] in response:
                            information = get_code_block(response, True, funct_name)
                            if information:
                                document_code = information["code"]
                                document_code = ("\n" + document_code).splitlines()
                                new_file.extend(document_code)
                                new_doc.extend(information["documentation"])
                            else:
                                code = ("\n" + func["code"]).splitlines()
                                new_file.extend(code)
                        else:
                            logger.info(__name__, f"Check response: {response}")
                            code = ("\n" + func["code"]).splitlines()
                            new_file.extend(code)

                    new_file.extend(code[end_line::])
                    new_code = "\n".join(new_file)
            else:
                pass

            write_code_to_path(full_path, new_code)

            if len(new_doc) > 1:
                for doctype, selected in formats.items():
                    if selected:
                        filename = (
                            (("readme_" + file).replace(extension, ".md"))
                            if doctype == "md"
                            else (("doc_" + file).replace(extension, ".docx"))
                        )
                        save_documentation(doc_path + filename, new_doc)
            else:
                pass
    except Exception as e:
        logger.info(__name__, f"{e}")
    finally:
        thread_semaphore.release()


async def exec_document(
    formats, method, chatbot_agent, file_manager: FileManager, frida_coder: FridaCoder
):
    """
    Documenting all the files using threads
    """
    logger.info(__name__, "Documenting files")
    file_manager.load_folder(file_manager.get_folder_path())

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
