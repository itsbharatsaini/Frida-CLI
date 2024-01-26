import os
import re
import datetime
from .languages.python import Python
from fridacli.config.env_vars import HOME_PATH


class FridaCoder:
    def __init__(self) -> None:
        self.code_files_dir = f"{HOME_PATH}/tmp/code"
        self.result_files_dir = f"{HOME_PATH}/tmp/results"
        self.code_blocks = []
        self.languages = {"python": {"extension": "py", "worker": Python()}}

    def run(self, response: str):
        if self.has_code_blocks(response):
            responses = []
            for code_block in self.code_blocks:
                language_info = self.get_language(code_block["language"])
                if language_info != None:
                    file_name = self.save_code_files(
                        code_block["code"], language_info["extension"]
                    )
                    language_info["worker"].run(
                        file_name=file_name, file_extesion=language_info["extension"]
                    )
                    file_path = os.path.join(self.result_files_dir, f"{file_name}.txt")
                    result = self.get_execution_result(file_path)
                    jump_point = result.find("\n")
                    status = result[:jump_point]
                    status = status if status == "ERROR" else "SUCCESS"
                    responses.append(
                        {   
                            "code": code_block["code"],
                            "status": status,
                            "description": code_block["description"],
                            "result": result if status == "SUCCESS" else result[jump_point:],
                        }
                    )
                else:
                    responses.append(
                        {   
                            "code": code_block["code"],
                            "status": "LANGNF"
                        }
                    )
            return responses
        return []

    def get_execution_result(self, file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            result = f.read()
            return result

    def extract_code(self, text):
        if len(self.code_blocks) == 0:
            code_pattern = re.compile(r"```(\w+)\n(.*?)```", re.DOTALL)
            matches = code_pattern.findall(text)

            self.code_blocks = [
                {
                    "language": match[0],
                    "code": match[1],
                    "description": match[1][: match[1].find("\n")],
                }
                for match in matches
            ]

            for block in self.code_blocks:
                first_line = block["code"][:block["code"].find("\n")]
                if "import" not in first_line and "def" not in first_line and "class" not in first_line:
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
