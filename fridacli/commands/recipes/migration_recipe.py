from fridacli.logger import Logger
from fridacli.chatbot import ChatbotAgent
from fridacli.file_manager import FileManager
from fridacli.frida_coder.languague.java import Java
from fridacli.file_manager.file import File
from .predefined_phrases import generate_recommendation_for_migration
from .utils import create_file, write_code_to_path
import re
import os
import threading

logger = Logger()

CODE_FROM_BLOCK = r"```(?:java)*(.*)```"
RECOMMENDATIONS_FROM_BLOCK = r"<recommendations>(.*)</recommendations>"
RECOMMENDATION = r"(?:(?:\d). \*\*(.*)\*\*:(.*))"
MAX_RETRIES = 2

LANGUAGES = {".java": Java()}


def extract_recommendations(text: str, funct_definition: str):
    """
    Extracts recommendations from given text based on a regular expression pattern.

    Parameters:
    - text (str): The input text from which recommendations are to be extracted.
    - funct_definition (str): The definition of the function for which recommendations are to be extracted.

    Returns:
    - list: A list of tuples representing formatted lines of recommendations.

    Raises:
    - Exception: If an error occurs while extracting recommendations, an exception is raised and logged.
    """
    try:
        lines = []
        rec = []

        # Iters over each line to find a well-written recommendation
        for line in text.splitlines():
            rec_match = re.match(RECOMMENDATION, line)
            if rec_match:
                rec.append(f"{rec_match.group(1)}. {rec_match.group(2)}")

        if rec != []:
            # If at least one recommendation is found, the subheader is added
            lines = [
                ("subheader", f"Function: {funct_definition}"),
                ("bold", "Recomendations:"),
            ]
            lines.append(("num_list", rec))
        else:
            logger.error(
                __name__,
                f"(extract_recommendations) Couldn't extract any recommendation for the function {funct_definition}",
            )

        return lines
    except Exception as e:
        logger.error(__name__, f"(extract_recommendations) {e}")


def extract_information(text: str, funct_definition: str):
    """
    Extracts code and recommendations information from the given text.

    Args:
        text (str): The text from which to extract information.
        funct_definition (str): The definition of the function.

    Returns:
        dict: A dictionary containing the extracted information. The dictionary
        has the following keys:
            - 'code': The extracted code from the text.
            - 'recommendations': The extracted recommendations related to the function.

    Raises:
        Exception: If there is an error during the extraction process.
    """
    try:
        information = {}
        # To extract the code block
        code_pattern = re.compile(CODE_FROM_BLOCK, re.DOTALL)
        # To extract the list of recommendations
        rec_pattern = re.compile(RECOMMENDATIONS_FROM_BLOCK, re.DOTALL)

        code_matches = code_pattern.findall(text)
        rec_matches = rec_pattern.findall(text)

        if code_matches == [] or rec_matches == []:
            logger.error(
                __name__,
                f"(extract_information) Couldn't extract recommendations and/or code from the response for the function {funct_definition}.",
            )
        else:
            information["code"] = code_matches[0]
            logger.info(
                __name__, f"(extract_information) Code extracted: {code_matches[0]}"
            )
            recommendations = extract_recommendations(rec_matches[0], funct_definition)
            if recommendations != []:
                information["recommendations"] = recommendations

        return information
    except Exception as e:
        logger.error(__name__, f"(extract_information) {e}")


def doc_migration_file(
    current_version: str,
    target_version: str,
    doc_path: str,
    file: File,
    thread_semaphore: threading.Semaphore,
    chatbot_agent: ChatbotAgent,
):
    """
    Document the migration of code in a file from a current version to a target version.

    Args:
        current_version (str): The current version of the code.
        target_version (str): The target version to migrate the code to.
        doc_path (str): The path to document the migration.
        file (File): The file object.
        thread_semaphore (threading.Semaphore): A semaphore to control the access to shared resources by multiple threads.
        chatbot_agent (ChatbotAgent): An agent for communicating with a chatbot.
    Raises:
        Exception: If there is an error during the extraction process.
    """
    thread_semaphore.acquire()
    try:
        extension = file.extension
        code = file.get_file_content()
        new_code = ""

        code_imports, imports_end_position = LANGUAGES[extension].extract_imports(code)
        new_imports = []

        functions, classes = LANGUAGES[extension].find_all_functions(code)
        retry = 1
        recommendations = [
            (
                "title",
                f"Recommendations to migrate from {current_version} to {target_version} for the file {file}",
            )
        ]

        new_code = code[: functions[0]["range"][0]]

        for i, func in enumerate(functions):
            funct_definition = func["definition"].replace("\n", "").replace("    ", "")
            funct_body = func["definition"] + "\n" + func["body"]
            is_constructor = func["is_constructor"]
            logger.info(
                __name__,
                f"(doc_migration_file) Code for the function {funct_definition}: {funct_body}",
            )
            prompt = generate_recommendation_for_migration(
                LANGUAGES[extension].name, current_version, target_version, funct_body
            )
            response = chatbot_agent.chat(prompt, True)

            while (
                ("```" not in response)
                and ("<recommendations>" not in response)
                and retry <= MAX_RETRIES
            ):
                logger.info(
                    __name__,
                    f"(doc_migration_file) Retry # {retry} for file {file} function {funct_definition} response: {response}",
                )
                response = chatbot_agent.chat(prompt, True)
                retry += 1
            retry = 1
            logger.info(
                __name__,
                f"(doc_migration_file) Final response for function {funct_definition}: {response}",
            )
            if ("```" in response) and ("<recommendations>" in response):
                information = extract_information(response, funct_definition)
                if LANGUAGES[extension].has_error(information["code"], is_constructor):
                    logger.error(
                        __name__,
                        f"(doc_migration_file) The code returned from the chat contained errors for function: {funct_definition}.",
                    )
                    new_code += (
                        funct_body
                        + code[func["range"][1] : functions[i + 1]["range"][0]]
                    )
                else:
                    imports, end_position = LANGUAGES[extension].extract_imports(
                        information["code"]
                    )
                    if imports != []:
                        for line in imports:
                            if line not in code_imports:
                                new_imports.append(line)
                        new_code += information["code"][end_position:]
                    else:
                        new_code += information["code"]
                    if i < (len(functions) - 1):
                        new_code += code[
                            func["range"][1] : functions[i + 1]["range"][0]
                        ]
                if "recommendations" in information.keys():
                    recommendations.extend(information["recommendations"])
            else:
                logger.error(
                    __name__,
                    f"(doc_migration_file) Couldn't generate tips for file {file}.",
                )
                new_code += (
                    funct_body + code[func["range"][1] : functions[i + 1]["range"][0]]
                )
        new_code += code[functions[-1]["range"][1] :]

        if new_imports != []:
            imports = "\n".join(new_imports)
            new_code = (
                new_code[:imports_end_position]
                + "\n"
                + imports
                + new_code[imports_end_position:]
            )

        # If there is new code to write
        if new_code != "":
            logger.info(
                __name__,
                f"(document_file) Writing the documented code for the file {file}",
            )
            write_code_to_path(
                os.path.join(file.path, "migrated_" + file.name),
                new_code,
                extension,
                False,
            )
        else:
            logger.error(
                __name__,
                f"(document_file) Could not write new code for file {file}",
            )

        if len(recommendations) > 1:
            create_file(
                os.path.join(
                    doc_path, f"migration_{file.name.replace(extension, '.docx')}"
                ),
                recommendations,
            )
        else:
            logger.error(
                __name__,
                f"(doc_migration_file) Couldn't generate tips for file {file}.",
            )
    except Exception as e:
        logger.error(__name__, f"(doc_migration_file) Error in file: {file}: {e}")
    finally:
        thread_semaphore.release()


async def exec_migration_file(
    language: str,
    current_version: str,
    target_version: str,
    doc_path: str,
    chatbot_agent: ChatbotAgent,
    file_manager: FileManager,
):
    """
    Executes migration files from current_version to target_version.

    Args:
        language (str): The language of the migration files.
        current_version (str): The current version of the migration files.
        target_version (str): The target version of the migration files.
        doc_path (str): The path to the migration files.
        chatbot_agent (ChatbotAgent): The chatbot agent.
        file_manager (FileManager): The file manager.
        frida_coder (FridaCoder): The Frida coder.

    Raises:
        Exception: If there is an error during the extraction process.

    """
    logger.info(
        __name__,
        f"(exec_migration_file) Generating migration file from {current_version} to {target_version}",
    )
    # Loading current directory
    file_manager.load_folder(file_manager.get_folder_path())

    files = file_manager.get_files()
    thread_semaphore = threading.Semaphore(5)

    threads = []
    logger.info(__name__, f"size: {len(files)}")
    for file in files:
        extension = file.extension
        # Verifies that the current file is from the expected language
        if extension in LANGUAGES.keys() and LANGUAGES[extension].name == language:
            logger.info(__name__, f"(exec_migration_file) I'll work on file {file}")
            thread = threading.Thread(
                target=doc_migration_file,
                args=(
                    current_version,
                    target_version,
                    doc_path,
                    file,
                    thread_semaphore,
                    chatbot_agent,
                ),
            )
            threads.append(thread)
            thread.start()

    # Joining all the threads
    for thread in threads:
        thread.join()
