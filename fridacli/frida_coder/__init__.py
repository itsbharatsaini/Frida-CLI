import os
import re
import datetime
from fridacli.frida_coder.languague.python import Python
from fridacli.config import HOME_PATH, SUPPORTED_PROGRAMMING_LANGUAGES, FRIDA_DIR_PATH
from .exception_message import ExceptionMessage
from fridacli.file_manager import FileManager
from fridacli.logger import Logger
logger = Logger()


class FridaCoder:
    def __init__(self) -> None:
        self.code_files_dir = f"{FRIDA_DIR_PATH}/fridatmp/code"
        self.result_files_dir = f"{FRIDA_DIR_PATH}/fridatmp/results"
        self.code_blocks = []
        self.__file_manager = FileManager()
        self.languages = {"python": {"extension": "py", "worker": Python()}}
        logger.info(
            __name__,
            f"""FridaCoder init
            Code files directory: {self.code_files_dir}
            Result files directory: {self.result_files_dir}
        """,
        )

    def prepare(self, response):
        """
            Prepare the code blocks to be run
        """
        logger.info(__name__, "(prepare) Preparing code blocks")
        self.code_blocks = []
        self.code_blocks = self.extract_code(response)
        return self.code_blocks
    
    def run(self, code_block, files_required):
        """
            Run the code block
        """
        logger.info(__name__, f"(run) Running code block with code block: {str(code_block)} and files required: {str(files_required)}")
        language_info = self.get_language(code_block["language"])
        logger.info(__name__, f"(run) Language info: {str(language_info)}")
        if language_info != None:
            """
            TODO:
                Insted of only one files_required should be able to work with multiple
            """
            path = ""
            if len(files_required) == 1:
                file_name = files_required[0]
                path = self.__file_manager.get_file_path(file_name)
            else:
                path = self.save_code_files(
                    code_block["code"], language_info["extension"]
                )
            logger.info(__name__, f"(run) The path {path}")
            exec_status, exec_result = language_info["worker"].run(
                path=path, file_extesion=language_info["extension"], file_exist=True
            )

            logger.info(__name__, f"(run) Exec status: {str(exec_status)} Exec result: {str(exec_result)}")
            try:
                jump_point = exec_result.find("\n")
                result_status = exec_result[:jump_point]
                status = (
                    ExceptionMessage.RESULT_ERROR
                    if exec_status == ExceptionMessage.EXEC_SUCCESS
                    or exec_status == ExceptionMessage.GET_RESULT_SUCCESS
                    and result_status == "ERROR"
                    else exec_status
                )
                # TODO Change the code_block["code"] when is a existing file
                payload = {
                    "code": code_block["code"],
                    "status": status,
                    "description": code_block["description"],
                    "result": (
                        exec_result
                        if status == ExceptionMessage.EXEC_SUCCESS
                        or exec_status == ExceptionMessage.GET_RESULT_SUCCESS
                        else exec_result[jump_point:]
                    ),
                }
                logger.info(__name__, f"(run) Payload: {str(payload)}")
                return payload
            except Exception as e:
                logger.error(__name__, f"(run) Error getting file path: {str(e)}")
        else:
            return {"code": code_block["code"], "status": "LANGNF"}

    def write_code_to_path(self, path: str, code: str):
        """
            Write the code to the given path
        """
        logger.info(__name__, f"(write_code_to_path) Writing code to path: {str(path)} with code: {str(code)}")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            logger.error(__name__, f"(write_code_to_path) Error writing code to path: {str(e)}")

    def get_code_from_path(self, path: str):
        """
            Get the code from the given path
        """
        logger.info(__name__, f"(get_code_from_path) Getting code from path: {str(path)}")
        try:
            with open(path, "r") as f:
                code = f.read()
                return code
        except Exception as e:
            logger.error(__name__, f"Error getting code from path: {str(e)}")

    def get_code_block(self, text):
        """
            Get the code block from the text
        """
        logger.info(__name__, f"(get_code_block) Getting code block from text: {str(text)}")
        try:
            code_pattern = re.compile(r"```(\w+)\n(.*?)```", re.DOTALL)
            matches = code_pattern.findall(text)
            code_blocks = [
                {
                    "language": match[0],
                    "code": match[1],
                    "description": match[1][: match[1].find("\n")],
                }
                for match in matches
            ]
            logger.info(__name__, f"(get_code_block) Code blocks: {str(code_blocks)}")
            return code_blocks
        except Exception as e:
            logger.error(__name__, f"(get_code_block) Error get code block from text using regex: {str(e)}")

    def extract_code(self, text):
        """
            Extract the code from the text
        """
        logger.info(__name__, f"(extract_code) Extracting code from text: {str(text)}")
        try:
            code_blocks = self.get_code_block(text)
            logger.info(__name__, f"(extract_code) Code blocks: {str(code_blocks)}")
            for block in code_blocks:
                first_line = block["code"][: block["code"].find("\n")]
                """
                TODO:
                    Improve the promt so the the response could have the description 
                
                """
                if (
                    "import" not in first_line
                    and "def" not in first_line
                    and "class" not in first_line
                    and "print" not in first_line
                ):
                    block["code"] = "\n".join(block["code"].split("\n")[1:])
            logger.info(__name__, f"(extract_code) Code block: {str(code_blocks)}")
            return code_blocks
        except Exception as e:
            logger.error(__name__, f"Error extracting code from text: {str(e)}")
            return []

    def has_code_blocks(self, text):
        """
            Check if the text has code blocks
        """
        logger.info(__name__, f"(has_code_blocks) Checking if the text has code blocks: {str(text)}")
        self.extract_code(text)
        if len(self.code_blocks) == 0:
            return False
        return True

    def save_code_files(self, code: str, extension: str = None):
        """
            Save the code files
        """
        logger.info(__name__, f"(save_code_files) Saving code files with code: {str(code)} and extension: {str(extension)}")
        try:
            time_format = "%Y-%m-%d_%H-%M-%S"
            formatted_time = datetime.datetime.now().strftime(time_format)
            file_name = f"{self.code_files_dir}/{formatted_time}.{extension}"
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(code)
            logger.info(__name__, f"(save_code_files) File name: {str(file_name)}")
            return file_name
        except Exception as e:
            logger.error(__name__, f"Error saving code files: {str(e)}")

    def get_language(self, language: str):
        """
            Get the language
        """
        logger.info(__name__, f"(get_language) Getting language: {str(language)}")
        try:
            if self.languages.get(language, -1) == -1:
                return None
            return self.languages[language]
        except Exception as e:
            logger.error(__name__, f"Error getting language: {str(e)}")
    
    def get_file_manager(self):
        """
            Get the file manager
        """
        logger.info(__name__, "(get_file_manager) Getting file manager")
        return self.__file_manager

    def clean(self):
        """
            Clean the code files
        """
        logger.info(__name__, "(clean) Cleaning code files")
        self.code_blocks = []

    def is_programming_language_extension(self, extension: str):
        """
            Check if the extension is a programming language
        """
        logger.info(__name__, f"(is_programming_language_extension) Checking if the extension is a programming language: {str(extension)}")
        logger.info(__name__, f"(is_programming_language_extension) Supported programming languages: {str(SUPPORTED_PROGRAMMING_LANGUAGES)}")
        return extension.lower() in SUPPORTED_PROGRAMMING_LANGUAGES

