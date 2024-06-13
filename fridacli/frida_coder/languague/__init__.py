from abc import ABC, abstractmethod
from fridacli.config import HOME_PATH, FRIDA_DIR_PATH
from fridacli.logger import Logger

logger = Logger()

class Language(ABC):
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