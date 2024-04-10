import re
import os
import threading
from fridacli.logger import Logger
from fridacli.frida_coder import FridaCoder
from fridacli.file_manager import FileManager
from .predefined_phrases import generate_document_prompt

logger = Logger()
MAX_RETRIES = 2

def get_code_block(text):
    try:
        code_pattern = re.compile(r"```(\w+)\n(.*?)```", re.DOTALL)
        matches = code_pattern.findall(text)
        code_blocks = [
            {
                "language": match[0],
                "code": match[1],
                "description": match[1][match[1].find("/// <summary>\n/// ") + len("/// <summary>\n/// "): match[1].find("\n/// </summary>")],
            }
            for match in matches
        ]

        logger.info(__name__, f"{code_blocks}")
        if code_blocks == []:
            logger.info(__name__, f"{text}")
        return code_blocks
    except Exception as e:
        pass
        #logger.error(__name__, f"Error get code block from text using regex: {e}")

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
            logger.info(__name__, f"line: {idx} Return: {function_match.group(1)} Name: {function_match.group(2)} Args: {function_match.group(3)}")
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
                    "code": "\n".join(current_function_lines),
                }
            )
            current_function = None
            current_function_lines = []
    return functions


def document_file(
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
            code = code.splitlines()
            functions = extract_functions(code)

            new_file = []

            start_line = functions[0]["start_line"]
            end_line = functions[-1]["end_line"]

            new_file.extend(code[0:start_line - 1])

            for func in functions:
                prompt = generate_document_prompt(func["code"], extension)
                response = chatbot_agent.chat(prompt, True)
                i = 0

                while ("```" not in response or "///" not in response) and i  < MAX_RETRIES:
                    response = chatbot_agent.chat(prompt, True)
                    i += 1

                if len(response) > 0:
                    code_blocks = get_code_block(response)
                    if len(code_blocks) > 0:
                        document_code = code_blocks[0]["code"]
                
                        document_code = ("\n" + document_code).splitlines()
                        new_file.extend(document_code)
                    else:
                        code = ("\n" + func["code"]).splitlines()
                        new_file.extend(code)
                else:
                    code = ("\n" + func["code"]).splitlines()
                    new_file.extend(code)


            new_file.extend(code[end_line::])
            new_code = "\n".join(new_file)

            full_path = file_manager.get_file_path(file)

            write_code_to_path(path = full_path, code = new_code)
    except Exception as e:
        logger.info(__name__, f"{e}")
    finally:
        thread_semaphore.release()


async def exec_document(
    chatbot_agent, file_manager: FileManager, frida_coder: FridaCoder
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