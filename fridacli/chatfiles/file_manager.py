import os
from .graph import Graph, Tree
from collections import Counter


class FileManager:
    """"""

    def __init__(self) -> None:
        self.__folder_status = False
        self.__folder_path: str = None
        self.__graph: Graph = None
        self.__tree: Tree = None
        self.__files = {}
        self.__extension_counter = Counter()

    def get_folder_status(self) -> bool:
        """"""
        return self.__folder_status

    def get_folder_path(self) -> str:
        """"""
        return self.__folder_path

    def get_files(self):
        return list(self.__files.keys())

    def get_file_path(self, name):
        return self.__files.get(name, -1)

    def get_file_content(self, name):
        path = self.__files.get(name, -1)
        with open(path, "r") as f:
            code = f.read()
            return code

    def __traverse(self, path, current_node):
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

    def load_folder(self, path: str) -> None:
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
        most_common_extensions = self.__extension_counter.most_common(1)
        top_three_extensions = [ext for ext, _ in most_common_extensions]
        project_type = ",".join(top_three_extensions)
        tree_str = self.__tree.print_directory()

        return (project_type, tree_str)

    def close_folder(self) -> None:
        """"""
        self.__folder_status = False
        self.__folder_path = None
