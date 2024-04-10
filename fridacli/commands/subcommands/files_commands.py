from fridacli.file_manager import FileManager
from fridacli.commands.subcommands.path_utilities import (
    check_samepath,
    check_valid_dir,
    change_directory,
    get_relative_path,
    get_current_dir,
)

from fridacli.commands.subcommands.predefined_phrases import (
    ERROR_PATH_NOT_GIVEN,
    ERROR_PATH_DOES_NOT_EXIST,
    GET_RESULT_SUCCESS,
)

from fridacli.logger import Logger
import os

logger = Logger()


def open_subcommand(path_to_open):
    """
    Command to open a file
    Input

    """
    if not path_to_open:
        return ERROR_PATH_NOT_GIVEN

    valid_path = check_valid_dir(path_to_open)

    if not valid_path:
        return ERROR_PATH_DOES_NOT_EXIST

    logger.info(__name__, f"Open command with path: {path_to_open}")
    file_manager = FileManager()
    active_folder = file_manager.get_folder_status()
    current_folder_active = check_samepath(get_current_dir(), path_to_open)

    project_type, tree_str = file_manager.load_folder(path=os.path.abspath(path_to_open))
    # change_directory(path_to_open)

    formatted_path = get_relative_path(path_to_open)

    return GET_RESULT_SUCCESS


def update_log_path(logs_path):
    Logger().update_log_paths(logs_path)
