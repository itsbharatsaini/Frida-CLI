from fridacli.logger import Logger
from fridacli.frida_coder import FridaCoder
from fridacli.file_manager import FileManager
import os
import threading

logger = Logger()
MAX_RETRIES = 2

LANGUAGE_EXTENSION = {
    ".java": "Java",
    ".py": "Python"
}


def doc_migration_file(
    current_version,
    target_version,
    doc_path,
    file,
    thread_semaphore,
    chatbot_agent,
    file_manager: FileManager,
    frida_coder: FridaCoder,
):
    thread_semaphore.acquire()
    try:
        pass

    except Exception as e:
        logger.info(__name__, f"Error in file: {file}: {e}")
    finally:
        thread_semaphore.release()


async def exec_migration_file(
    language,
    current_version,
    target_version,
    doc_path,
    chatbot_agent,
    file_manager: FileManager,
    frida_coder: FridaCoder,
):
    logger.info(__name__, f"Generating migration file from {current_version} to {target_version}")
    file_manager.load_folder(file_manager.get_folder_path())

    files = file_manager.get_files()
    thread_semaphore = threading.Semaphore(5)

    threads = []
    logger.info(__name__, f"size: {len(files)}")
    for file in files:
        _, extension = os.path.splitext(file)
        if frida_coder.is_programming_language_extension(extension) and extension in LANGUAGE_EXTENSION.keys() and LANGUAGE_EXTENSION[extension] == language:
            logger.info(__name__, f"I'll work on  file {file}")
            thread = threading.Thread(
                target=doc_migration_file,
                args=(
                    current_version,
                    target_version,
                    doc_path,
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
