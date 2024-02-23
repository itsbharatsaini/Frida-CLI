import os
import ast
import subprocess
from fridacli.fridaCoder.languages.languague import Language
from typing_extensions import override
from ..exceptionMessage import ExceptionMessage
from config.env_vars import get_config_vars
from fridacli.logger import Logger
from fridacli.interface.system_console import SystemConsole

system_console = SystemConsole()

logger = Logger()


class Python(Language):
    def __init__(self) -> None:
        super().__init__()
        self.__get_env()

    @override
    def run(self, path: None, file_extesion: str = None, file_exist: bool = False):
        """
        TODO:
            Change for all the code runs using file exisiting why aviod using python eval
        """
        preprocessed_code = ""
        result_path = f"{self.result_files_dir}/{path}.txt"
        code_path = f"{self.code_files_dir}/{path}.{file_extesion}"

        if file_exist:
            directory, old_filename = os.path.split(path)
            file_name, file_extension = os.path.splitext(old_filename)
            result_path = f"{self.result_files_dir}/{file_name}_tmp.txt"
            code_path = path
        result_status = None
        try:
            with open(code_path, encoding="utf-8") as fl:
                code = fl.read()
                os.makedirs(os.path.dirname(result_path), exist_ok=True)
                preprocessed_code = code
                if file_exist:
                    result_status = self.__execute_existing_code(code_path, result_path)
                else:
                    preprocessed_code = self.__preprocess_code(code, result_path)
                    result_status = self.__execute_code(preprocessed_code)
            return self.__build_result(result_path, result_status)
        except Exception as e:
            logger.error(__name__, f"Error running: {e}")

    def __get_env(self):
        try:
            env_vars = get_config_vars()
            if "PYTHON_ENV_PATH" in env_vars:
                self.__PYTHON_ENV_PATH = env_vars["PYTHON_ENV_PATH"]
            else:
                self.__PYTHON_ENV_PATH = ""
        except Exception as e:
            logger.error(__name__, f"Error getting enviroment path: {e}")

    def __build_result(self, result_path, result_status):
        if result_status == ExceptionMessage.EXEC_ERROR:
            return (result_status, None)
        result = self.__get_execution_result(result_path)
        if result == None:
            return (ExceptionMessage.GET_RESULT_ERROR, None)
        return (ExceptionMessage.GET_RESULT_SUCCESS, result)

    def __execute_code(self, code: str):
        try:
            """
            [Deplicated]
            TODO:
                When a funtion is exectuted and the is used in different blocks it can be used the problem
                is that for diferent prompts shouldn't have the same funtion

                Insted of globals() use another namespace to not compromise the exactution in runtime
            """

            exec(code, globals())
            return ExceptionMessage.EXEC_SUCCESS
        except:
            return ExceptionMessage.EXEC_ERROR

    def __execute_existing_code(self, code_path: str, result_path):

        if len(self.__PYTHON_ENV_PATH) == 0:
            system_console.notification(
                "Python env path not configurated, use `frida config --python_env`"
            )
            with open(result_path, "w") as f:
                f.write("No env configured")
            return ExceptionMessage.EXEC_SUCCESS

        try:
            """
            TODO:
                and also python3 or a posibility to change the variable name
            """
            result = subprocess.run(
                [self.__PYTHON_ENV_PATH, code_path], capture_output=True, text=True
            )
            with open(result_path, "w") as f:
                f.write(result.stdout)
            return ExceptionMessage.EXEC_SUCCESS
        except:
            return ExceptionMessage.EXEC_ERROR

    def __get_execution_result(self, file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                result = f.read()
                return result
        except Exception as e:
            logger.error(__name__, f"Error getting execution result: {e}")
            return None

    def __preprocess_code(self, code, path):
        return self.__use_template(code, path)

    def __use_template(self, code, file_name):
        try:
            code_lines = code.split("\n")
            code_lines = [f"            {c}" for c in code_lines]
            code = "\n".join(code_lines)
            code = f"""
from contextlib import redirect_stdout
import traceback
with open(r'{file_name}', 'w', encoding='utf-8') as file:
    with redirect_stdout(file):
        try:
{code}
        except Exception as e:
            traceback_str = traceback.format_exc()
            file.write('ERROR\\n')
            file.write(traceback_str)
                
            """
            code_lines = code.split("\n")
            code_lines = [c for c in code_lines if c.strip() != ""]
            code = "\n".join(code_lines)
            return code
        except Exception as e:
            logger.error(__name__, f"Error using template: {e}")
