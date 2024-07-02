from abc import ABC, abstractmethod
from fridacli.config import FRIDA_DIR_PATH
from fridacli.logger import Logger

logger = Logger()

class BaseLanguage(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.result_files_dir = f"{FRIDA_DIR_PATH}/tmp/results"
        self.code_files_dir = f"{FRIDA_DIR_PATH}/tmp/code"
        logger.info(__name__, f"""Language init
            Result files directory: {self.result_files_dir}
            Code files directory: {self.code_files_dir}
        """)

    @abstractmethod
    def run(self, code):
        raise NotImplementedError("run method must be overridden")
    
    @abstractmethod
    def find_all_functions(self, code):
        raise NotImplementedError("find_all_functions method must be overriden")
    
    @abstractmethod
    def extract_documentation(self, comments):
        raise NotImplementedError("extract_documentation method must be overriden")
    
    @abstractmethod
    def extract_doc_all_functions(self, code):
        raise NotImplementedError("extract_doc_all_functions method must be overriden")
    
    @abstractmethod
    def extract_doc_single_function(self, code, funct_definition):
        raise NotImplementedError("extract_doc_one_function")