import os
import re
from fridacli.interface.system_console import SystemConsole
import fridacli.commands.subcommands.predefined_phrases as predefined_phrases


""""""
system = SystemConsole()
#graph = Graph()


def exec_angular_voyager(path):
    """
    1) Detect if the path is a angular project
    2) Traverse the files recursively and create a graph with the project structure
    """

    if is_angular_proyect(path):
        system.steps_notification(predefined_phrases.ANGULAR_PROJECT_DETECTED)
        traverse_dir(path)
        #graph.construct()
        #print("nodes =", graph.get_nodes())
        #print("graph =", graph.get_graph())
        system.steps_notification(predefined_phrases.ANGULAR_PROJECT_GRAPH_CONSTRUCTED)
    else:
        system.steps_notification(predefined_phrases.ANGULAR_PROJECT_NOT_DETECTED(path))


def is_angular_proyect(path):
    """
    Checks whether the Angular configuration file (angular.json or angular-cli.json)
    exists in the specified path.

    Args:
        path (str): The path to check for the Angular configuration file.

    Returns:
        bool: True if either angular.json or angular-cli.json exists, False otherwise.
    """
    angular_json_path = os.path.join(path, "angular.json")
    angular_cli_json_path = os.path.join(path, "angular-cli.json")
    dot_angular_cli_json_path = os.path.join(path, ".angular-cli")

    return os.path.exists(angular_json_path) or os.path.exists(angular_cli_json_path) or dot_angular_cli_json_path


def is_dir(path):
    """
    Check if the given path corresponds to a directory.

    Parameters:
    - path (str): The path to be checked.

    Returns:
    - bool: True if the path represents a directory, False otherwise.

    Example:
    >>> is_dir('/path/to/directory')
    True
    """
    return os.path.isdir(path)


def get_imports_from_file(path):
    """
    Extract import statements from the content of a given file.

    Parameters:
    - path (str): The path to the file.

    Returns:
    - list: A list of imported module names.

    Example:
    >>> get_imports_from_file('/path/to/source/file.js')
    ['module1', 'module2']

    Note:
    - This function reads the content of the specified file and uses a regular expression pattern
      to identify and extract import statements. The pattern is designed for import statements
      that use the ES6 syntax, such as 'import { module } from 'module';'.
    """
    with open(path, "r", encoding="utf-8") as file:
        file_content = file.read()

    pattern = r"^\s*import\s*{[^}]+}\s*from\s*\'([^\']+)\';"

    matches = re.findall(pattern, file_content, re.MULTILINE)
    return matches


def remove_extension(file_path):
    """
    Remove the file extension from the given file path.

    Parameters:
    - file_path (str): The full path to the file including its name and extension.

    Returns:
    - str: The path without the file extension.

    Example:
    >>> remove_extension('/path/to/file/example.txt')
    '/path/to/file/example'
    """
    directory, filename = os.path.split(file_path)
    name, _ = os.path.splitext(filename)
    path_without_extension = os.path.join(directory, name)
    return path_without_extension


def calculate_id(path):
    """
    Calculate an identifier for a given file path by removing its extension and refining it based on its location
    within a typical source structure.

    Parameters:
    - path (str): The full path to the file.

    Returns:
    - str: The calculated identifier.

    Example:
    >>> calculate_id('/path/to/project/src/app/module/file.ts')
    'src/app/module/file'
    """
    path = remove_extension(path)
    src_loc = [loc for loc in [path.find("src"), path.find("app")] if loc != -1]
    path = path[min(src_loc)::] if len(src_loc) else path
    path = path.replace("//", "/")
    return path


def traverse_dir(path):
    """
    Traverse recursively the angular proyect to create the graphs

    Parameters:
    - path (str): The full path to the file.

    Returns:
    - None
    """
    files_list = os.listdir(path)
    #node = Node(is_dir=is_dir(path), name=path, files_name=files_list)
    #traverse(path, node)


def traverse(path, node):
    """
    
    files_list = os.listdir(path)
    for file in files_list:
        new_path = os.path.join(path, file)
        is_dir_value = is_dir(new_path)
        #file_node = Node(is_dir=is_dir_value, name=new_path, parent=node)
        #node.add_adyecency(file_node)
        if is_dir_value:
            #traverse(new_path, file_node)
        else:
            extension = file.split(".")[-1]
            if extension in ("js", "ts"):
                imports = get_imports_from_file(new_path)
                id = calculate_id(new_path)
                imports = [calculate_id(i) for i in imports]
                adj_node = AdjNode(id=id, raw_connections=imports)
                graph.add_node(id, adj_node)
    """
