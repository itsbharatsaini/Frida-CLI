from collections import Counter
from .graph import Tree
import os

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
            self.__files = {}
            self.__extension_counter = Counter()
            self._initialized = True

    def get_files(self):
        try:
            return list(self.__files.keys())
        except Exception as e:
            pass
            #logger.error(__name__, f"Error getting files: {e}")
    def get_file_path(self, name):
        try:
            return self.__files.get(name, -1)
        except Exception as e:
            pass
            #logger.error(__name__, f"Error getting file path: {e}")
        
    def get_file_content(self, name):
        try:
            path = self.__files.get(name, -1)
            with open(path, "r") as f:
                code = f.read()
                return code
        except Exception as e:
            pass
            #logger.error(__name__, f"Error getting file content: {e}")

    def __traverse(self, path, current_node):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                if os.path.isdir(item_path):
                    child_node = Tree(item_path)
                    current_node.add_children(child_node)
                    self.__traverse(item_path, child_node)
                else:
                    self.__files[item] = item_path

                    item_parts = item.split(".")
                    if len(item_parts) == 2:
                        extension = item_parts[1]
                        self.__extension_counter[extension] += 1
                        current_node.add_children(Tree(item_path))
        except Exception as e:
            pass
            #logger.error(__name__, f"Error traversing: {e}")

    def __build_directory_tree(self, path):
        """
        Traverse recursively a directory to create the graphs

        Parameters:
        - path (str): The full path to the file.

        Returns:
        - None
        """
        root_node = Tree(path)
        self.__traverse(path, root_node)
        return root_node


    def load_folder(self, path: str):
        """
        TODO:
            Improve print directory Tree
                -Add markdown to the directories names
                -When a directory is empty is printed as a file and the next dir
                have wrong identation
        """
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
            pass
            #logger.error(__name__, f"Error loading folder: {e}")
        return (project_type, tree_str)

    def close_folder(self) -> None:
        """"""
        self.__folder_status = False
        self.__folder_path = None

    def set_dir(self, file_directory: str) -> None:
        self.__folder_path = file_directory

    def get_folder_status(self) -> bool:
        return self.__folder_status

    def get_folder_path(self) -> str:
        return str(self.__folder_path)

