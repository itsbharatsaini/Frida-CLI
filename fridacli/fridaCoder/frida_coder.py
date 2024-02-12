import os
import re
import datetime
from .languages.python import Python
from fridacli.config.env_vars import HOME_PATH
from .exceptionMessage import ExceptionMessage


class FridaCoder:
    def __init__(self, file_manager) -> None:
        self.code_files_dir = f"{HOME_PATH}/tmp/code"
        self.result_files_dir = f"{HOME_PATH}/tmp/results"
        self.code_blocks = []
        self.__file_manager = file_manager
        self.languages = {"python": {"extension": "py", "worker": Python()}}

    def prepare(self, response):
        self.code_blocks = []
        self.code_blocks = self.extract_code(response)
        return self.code_blocks

    def run(self, code_block, files_required):
        language_info = self.get_language(code_block["language"])
        if language_info != None:
            """
            TODO:
                Insted of only one files_required should be able to work with multiple
            """
            if len(files_required) == 1:
                file_name = files_required[0]
                path = self.__file_manager.get_file_path(file_name)
                exec_status, exec_result = language_info["worker"].run(
                    path=path, file_exist=True
                )
            else:
                file_name = self.save_code_files(
                    code_block["code"], language_info["extension"]
                )
                exec_status, exec_result = language_info["worker"].run(
                    path=file_name, file_extesion=language_info["extension"]
                )
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
            return {
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

        else:
            return {"code": code_block["code"], "status": "LANGNF"}

    def write_code_to_path(self, path: str, code: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

    def get_code_from_path(self, path: str):
        with open(path, "r") as f:
            code = f.read()
            return code

    def get_code_block(self, text):
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
        return code_blocks

    def extract_code(self, text):
        if len(self.code_blocks) == 0:
            self.code_blocks = self.get_code_block(text)

            for block in self.code_blocks:
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

            return self.code_blocks
        return self.code_blocks

    def has_code_blocks(self, text):
        self.extract_code(text)
        if len(self.code_blocks) == 0:
            return False
        return True

    def save_code_files(self, code: str, extension: str = None):
        time_format = "%Y-%m-%d_%H-%M-%S"
        formatted_time = datetime.datetime.now().strftime(time_format)
        file_name = f"{self.code_files_dir}/{formatted_time}.{extension}"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        return formatted_time

    def get_language(self, language: str):
        if self.languages.get(language, -1) == -1:
            return None
        return self.languages[language]

    def clean(self):
        self.code_blocks = []

    def is_programming_language_extension(self, extension: str):
        programming_language_extensions = [
            ".py",
            ".asp" ".java",
            ".cpp",
            ".c",
            ".cs",
            ".js",
            ".html",
            ".css",
            ".php",
            ".rb",
            ".swift",
            ".go",
            ".lua",
            ".pl",
            ".r",
            ".sh",
        ]
        return extension.lower() in programming_language_extensions
