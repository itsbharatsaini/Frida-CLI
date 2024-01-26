import os
import ast
from fridacli.fridaCoder.languages.languague import Language
from typing_extensions import override


class Python(Language):
    def __init__(self) -> None:
        super().__init__()

    @override
    def run(self, file_name: None, file_extesion: None):
        preprocessed_code = ""
        with open(f"{self.code_files_dir}/{file_name}.{file_extesion}", encoding='utf-8') as fl:
            code = fl.read()
            try:
                preprocessed_code = self.__preprocess_code(code, file_name)
                self.__execute_code(preprocessed_code)
            except Exception as e :
                print(e)
        return
        

    def __execute_code(self, code):
        exec(code, globals())

    def __preprocess_code(self, code, file_name):
        file_name = f"{self.result_files_dir}/{file_name}.txt"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
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
