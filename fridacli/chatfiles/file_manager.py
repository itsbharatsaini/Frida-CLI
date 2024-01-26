class FileManager:
    """"""

    def __init__(self) -> None:
        self.__folder_status = False
        self.__folder_path: str = None

    def get_folder_status(self) -> bool:
        """"""
        return self.__folder_status

    def get_folder_path(self) -> str:
        """"""
        return self.__folder_path

    def load_folder(self, path: str) -> None:
        """"""
        self.__folder_status = True
        self.__folder_path = path

    def close_folder(self) -> None:
        """"""
        self.__folder_status = False
        self.__folder_path = None
