import os
import threading
from fridacli.logger import Logger
from fridacli.frida_coder import FridaCoder
from fridacli.file_manager import FileManager
from .predefined_phrases import generate_document_prompt

logger = Logger()

def document_file(file, thread_semaphore, chatbot_agent, file_manager: FileManager, frida_coder: FridaCoder):
    thread_semaphore.acquire()
    try:
        _, extension = os.path.splitext(file)
        if frida_coder.is_programming_language_extension(extension):
            logger.info(__name__, f"working on {file}")
            full_path = file_manager.get_file_path(file)
            code = frida_coder.get_code_from_path(full_path)
            prompt = generate_document_prompt(code)
            response = chatbot_agent.chat(prompt, True)
            logger.info(__name__, f"Response len {prompt}")
            
            if len(response) > 0 :
                code_blocks = frida_coder.get_code_block(response)
                if len(code_blocks) > 0:
                    document_code = code_blocks[0]["code"]
                    frida_coder.write_code_to_path(full_path, document_code)
    finally:
        thread_semaphore.release()



async def exec_document(chatbot_agent, file_manager: FileManager, frida_coder: FridaCoder):
    """
    Documenting all the files using threads
    """
    logger.info(__name__, "Documenting files")
    files =  file_manager.get_files()
    thread_semaphore = threading.Semaphore(5)

    threads = []
    logger.info(__name__, f"size: {len(files)}")
    for file in files:
        thread = threading.Thread(target=document_file, args = (file, thread_semaphore, chatbot_agent, file_manager, frida_coder,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


        


