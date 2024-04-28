import re
import os
import threading
from docx import Document
from mdutils.mdutils import MdUtils
from fridacli.logger import Logger
from fridacli.frida_coder import FridaCoder
from fridacli.file_manager import FileManager
from .predefined_phrases import generate_document_for_funct_prompt, generate_full_document_prompt

logger = Logger()
MAX_RETRIES = 2

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
                doc.add_paragraph(text, style='List Bullet')

        doc.save(path)
    else:
        mdFile = None
        bullets = []
        for format, text in lines:
            if format == "title":
                mdFile = MdUtils(file_name=path, title=text)
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

        logger.info(__name__, "Creating doc...")
        mdFile.create_md_file()

def extract_documentation(information, one_function, funct_name):
    lines = []
    first_parameter = True
    first_return = True
    first_exception = True

    if one_function:
        function = []
        for idx, line in enumerate(information["code"].splitlines(), 1):
            try:
                param_match = re.match(r"^\s*///\s*<\s*param\s*name\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</param>\s*$", line)
                returns_match = re.match(r'^\s*///\s*<\s*returns\s*>([\w\.\-\s<>=\"/{}]*)</returns>\s*$', line)
                exception_match = re.match(r'^\s*///\s*<\s*exception\s*cref\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</exception>\s*$', line)
                function_match = re.match(r'^\s*(?:(?:public|private|protected|internal|static|async|unsafe|sealed|new|override|virtual|abstract)\s+)+(?:[\w<>\[\],\.]+\s+)+([\w_]+)\s*\((?:.*)\)\s*(?:where.*)?\s*$', line)

                if param_match:
                    if first_parameter:
                        function.append(("bold", "Arguments:"))
                        function.append(("bullet", f"{param_match.group(1)}. {param_match.group(2)}"))
                        first_parameter = False
                    else:
                        function.append(("bullet", f"{param_match.group(1)}. {param_match.group(2)}"))
                    
                elif returns_match:
                    if first_return:
                        function.append(("bold", "Return:"))
                        function.append(("bullet", f"{returns_match.group(1)}"))
                        first_return = False
                    else:
                        function.append(("bullet", f"{returns_match.group(1)}"))

                    logger.info(__name__, f"return: {returns_match.group(1)}")
                elif exception_match:
                    if first_exception:
                        function.append(("bold", "Exception:"))
                        function.append(("bullet", f"{exception_match.group(1)}. {exception_match.group(2)}"))
                        first_exception = False
                    else:
                        function.append(("bullet", f"{exception_match.group(1)}. {exception_match.group(2)}"))
                elif function_match:
                    lines.extend([("subheader", f"Function: {function_match.group(1)}"), ("bold", "Description:"), ("text", information["description"].rstrip())])
                    lines.extend(function)
                    function = []
                    logger.info(__name__, f"name {function_match.group(1)}")
    
            except Exception as e:
                logger.error(__name__, f"func: {function['name_of_function']} | idx: {idx} | line: {line} error: {e}")
    else:
        lines = [("subheader", f"Function: {funct_name}"), ("bold", "Description:"), ("text", information['description'].rstrip())]

        for idx, line in enumerate(information["code"].splitlines(), 1):
            try:
                param_match = re.match(r"^\s*///\s*<\s*param\s*name\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</param>\s*$", line)
                returns_match = re.match(r'^\s*///\s*<\s*returns\s*>([\w\.\-\s<>=\"/{}]*)</returns>\s*$', line)
                exception_match = re.match(r'^\s*///\s*<\s*exception\s*cref\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</exception>\s*$', line)

                if param_match:
                    if first_parameter:
                        lines.append(("bold", "Arguments:"))
                        lines.append(("bullet", f"{param_match.group(1)}. {param_match.group(2)}"))
                        first_parameter = False
                    else:
                        lines.append(("bullet", f"{param_match.group(1)}. {param_match.group(2)}"))
                    
                elif returns_match:
                    if first_return:
                        lines.append(("bold", "Return:"))
                        lines.append(("bullet", f"{returns_match.group(1)}"))
                        first_return = False
                    else:
                        lines.append(("bullet", f"{returns_match.group(1)}"))

                    logger.info(__name__, f"return: {returns_match.group(1)}")
                elif exception_match:
                    if first_exception:
                        lines.append(("bold", "Exception:"))
                        lines.append(("bullet", f"{exception_match.group(1)}. {exception_match.group(2)}"))
                        first_exception = False
                    else:
                        lines.append(("bullet", f"{exception_match.group(1)}. {exception_match.group(2)}"))
    
            except Exception as e:
                logger.error(__name__, f"func: {function['name_of_function']} | idx: {idx} | line: {line} error: {e}")
    
    return lines

def get_code_block(text, one_function, funct_name = None):
    try:
        code_pattern = re.compile(r"```([\w#]*)\s*([\w.;\s]*\s*(?:///\s*<\s*summary\s*>\s*///\s*([\w,.:/\s]*)///\s*<\s*/\s*summary\s*>)*\s*.*)```", re.DOTALL)
        matches = code_pattern.findall(text)
        
        if matches == []:
            logger.info(__name__, f"Revisar  2: {text}")
        else:
            for match in matches:
                logger.info(__name__, f"0: {match[0]} 1: {match[1]} 2: {match[2]}")
            information = {
                    "language": matches[0][0],
                    "code": matches[0][1],
                    "description": matches[0][2].replace("/", "").replace("`", "")
                }
            
            lines = extract_documentation(information, one_function, funct_name)
            information["documentation"] = lines
            logger.info(__name__, lines)
            return information
    except Exception as e:
        logger.error(__name__, f"Error get code block from text using regex: {e}")

def write_code_to_path(path: str, code: str):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        pass
        #logger.error(__name__, f"Error writing code to path: {e}")

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
            #logger.info(__name__, f"line: {idx} Return: {function_match.group(1)} Name: {function_match.group(2)} Args: {function_match.group(3)}")
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
            doc_path = ''.join(full_path.split(file)[:-1])
            
            code = frida_coder.get_code_from_path(full_path)
            num_lines = code.count('\n')

            new_file = []
            new_doc = [("title", f"Documentation of the file '{file}'")]

            i = 1

            if method == "Quick":

                if num_lines <= 300:
                    logger.info(__name__, f"Extension: {extension} | Method: {method}")
                    prompt = generate_full_document_prompt(code, extension)
                    response = chatbot_agent.chat(prompt, True)

                    while ("```" not in response or "///" not in response) and i <= MAX_RETRIES:
                        logger.info(__name__, f"Retry # {i} for file {file}")
                        response = chatbot_agent.chat(prompt, True)
                        i += 1
                    
                    if ("```" in response and "///" in response):
                        information = get_code_block(response, True)
                        if information:
                            document_code = information["code"]
                    else:
                        logger.info(__name__, f"Revisar 1: {response}")
                    
                else:
                    logger.info(__name__, f"else  - Extension: {extension} | Method: {method}")
                    code = code.splitlines()
                    functions = extract_functions(code)

                    start_line = functions[0]["start_line"]
                    end_line = functions[-1]["end_line"]

                    new_file.extend(code[0:start_line - 1])

                    logger.info(__name__, functions)

                    for func in functions:
                        funct_name = func["name_of_function"]
                        prompt = generate_document_for_funct_prompt(func["code"], extension)
                        response = chatbot_agent.chat(prompt, True)

                        while ("```" not in response or "///" not in response) and i <= MAX_RETRIES:
                            logger.info(__name__, f"Retry # {i} for file {file} function {funct_name}")
                            response = chatbot_agent.chat(prompt, True)
                            i += 1

                        if ("```" in response and "///" in response):
                            information = get_code_block(response, False, funct_name)
                            if information:
                                document_code = information["code"]
                                document_code = ("\n" + document_code).splitlines()
                                new_file.extend(document_code)
                                
                                documentation = get_documentation(information[0], func)
                                new_doc.extend(documentation)
                            else:
                                code = ("\n" + func["code"]).splitlines()
                                new_file.extend(code)
                        else:
                            code = ("\n" + func["code"]).splitlines()
                            new_file.extend(code)


                    new_file.extend(code[end_line::])
                    new_code = "\n".join(new_file)

            write_code_to_path(full_path, new_code)

            for doctype, selected in formats.items():
                if selected:
                    filename = (("readme_" + file).replace(extension, ".md")) if doctype == "md" else (("doc_" + file).replace(extension, ".docx"))
                    save_documentation(doc_path + filename, new_doc)
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