from collections import Counter
from .graph import Tree
import os
from .file import File
from fridacli.logger import Logger

logger = Logger()


class FileManager:
    """
    Singleton to manage the project open files
    """
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(FileManager, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.__folder_path = ""
            self.__folder_status = False
            self.__tree = None
            self.__files = []
            self.__extension_counter = Counter()
            self._initialized = True

    def get_files(self):
        """
            Get the files in the project
        """
        logger.info(__name__, f"(get_files) Getting files: {[file.name for file in self.__files]}")
        try:
            return self.__files
        except Exception as e:
            logger.error(__name__, f"(get_files) Error getting files: {str(e)}")

    def __traverse(self, path, current_node):
        """
            Traverse recursively a directory to create the graphs
        """

        logger.info(__name__, f"(__traverse) Traversing path: {path} current_node: {current_node}")
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                if os.path.isdir(item_path):
                    child_node = Tree(item_path)
                    current_node.add_children(child_node)
                    self.__traverse(item_path, child_node)
                else:
                    self.__files.append(File(item, path))

                    if self.__files[-1].has_extension():
                        self.__extension_counter[self.__files[-1].extension] += 1
                        current_node.add_children(Tree(item_path))
        except Exception as e:
            logger.error(__name__, f"(__traverse) Error traversing: {str(e)}")

    def __build_directory_tree(self, path):
        """
        Traverse recursively a directory to create the graphs

        Parameters:
        - path (str): The full path to the file.

        Returns:
        - None
        """

        logger.info(__name__, f"(__build_directory_tree) Building directory tree path: {path}")
        root_node = Tree(path)
        self.__files = []
        self.__traverse(path, root_node)
        logger.info(__name__, f"(__build_directory_tree) Files: {[file.name for file in self.__files]}")
        return root_node


    def load_folder(self, path: str):
        """
        TODO:
            Improve print directory Tree
                -Add markdown to the directories names
                -When a directory is empty is printed as a file and the next dir
                have wrong identation
        """
        logger.info(__name__, f"(load_folder) Loading folder path: {path}")
        self.__folder_status = True
        self.__folder_path = path
        # know the project type
        self.__tree = self.__build_directory_tree(self.__folder_path)
        try:
            most_common_extensions = self.__extension_counter.most_common(1)
            top_three_extensions = [ext for ext, _ in most_common_extensions]
            project_type = ",".join(top_three_extensions)
            tree_str = self.__tree.print_directory()
        except Exception as e:
            logger.error(__name__, f"(load_folder) Error loading folder: {str(e)}")
        return (project_type, tree_str)

    def close_folder(self) -> None:
        """
            Close the current project
        """
        logger.info(__name__, "(close_folder) Closing folder")
        self.__folder_status = False
        self.__folder_path = None

    def set_dir(self, file_directory: str) -> None:
        """
            Set the directory of the project
        """
        logger.info(__name__, f"(set_dir) Setting directory: {file_directory}")
        self.__folder_path = file_directory

    def get_folder_status(self) -> bool:
        """
            Get the status of the folder
        """
        logger.info(__name__, f"(get_folder_status) Getting folder status: {str(self.__folder_status)}")
        return self.__folder_status

    def get_folder_path(self) -> str:
        """
            Get the path of the folder
        """
        logger.info(__name__, f"(get_folder_path) Getting folder path: {str(self.__folder_path)}")
        return str(self.__folder_path)

