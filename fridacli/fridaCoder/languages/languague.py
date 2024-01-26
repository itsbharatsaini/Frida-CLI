from abc import ABC, abstractmethod
from fridacli.config.env_vars import HOME_PATH

class Language(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.result_files_dir = f"{HOME_PATH}/tmp/results"
        self.code_files_dir = f"{HOME_PATH}/tmp/code"

    @abstractmethod
    def run(self, code):
        raise NotImplementedError("run method must be overridden")