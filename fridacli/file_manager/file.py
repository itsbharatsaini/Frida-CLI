from fridacli.logger import Logger
import os

logger = Logger()


class File:
    def __init__(self, name: str, path: str) -> None:
        self.__name = name
        self.__path = path
        self.__extension = self.__extract_extension(name)

    @property
    def name(self):
        return self.__name

    @property
    def path(self):
        return self.__path

    @property
    def extension(self):
        return self.__extension

    def __extract_extension(self, name: str) -> str | None:
        try:
            return "." + name.split(".")[-1]
        except Exception as e:
            return None

    def __str__(self) -> str:
        return self.__name

    def has_extension(self) -> bool:
        return self.__extension is not None

    def get_file_path(self) -> str:
        """
        Get the file path.
        """
        logger.info(
            __name__, f"(get_file_path) Getting file content name: {self.__name}"
        )
        try:
            return os.path.join(self.__path, self.__name)
        except Exception as e:
            logger.error(
                __name__, f"(get_file_path) Error getting file content: {str(e)}"
            )

    def get_file_content(self) -> str:
        """
        Get the file content of a file in the project
        """
        logger.info(
            __name__, f"(get_file_content) Getting file content name: {self.__name}"
        )
        try:
            full_path = os.path.join(self.__path, self.__name)
            with open(full_path, "r") as f:
                code = f.read()
                return code
        except Exception as e:
            logger.error(
                __name__, f"(get_file_content) Error getting file content: {str(e)}"
            )
