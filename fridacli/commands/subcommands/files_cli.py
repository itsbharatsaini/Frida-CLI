from fridacli.chatfiles.file_manager import FileManager
from fridacli.chatfiles.path_utilities import (
    check_samepath,
    check_valid_dir,
    change_directory,
    get_relative_path,
    get_current_dir,
)
from fridacli.interface.system_console import SystemConsole
from fridacli.predefined_phrases.chat_command import (
    CONFIRM_RELOAD_PROJECT,
    CONFIRM_OPEN_NEW_PROJECT,
    ERROR_PATH_DOES_NOT_EXIST,
    WARNING_ARGUMENT_REQUIRED,
)


def open_subcommand(*args, **kwargs):
    """"""
    system_console: SystemConsole = kwargs.get("system_console")
    file_manager: FileManager = kwargs.get("file_manager")

    if not args:
        system_console.notification(WARNING_ARGUMENT_REQUIRED("path"))
        return

    path_to_open = args[0]
    valid_path = check_valid_dir(path_to_open)

    if not valid_path:
        system_console.notification(ERROR_PATH_DOES_NOT_EXIST(path_to_open))
        return

    active_folder = file_manager.get_folder_status()
    current_folder_active = check_samepath(get_current_dir(), path_to_open)

    if active_folder:
        confirm_message = (
            CONFIRM_RELOAD_PROJECT
            if current_folder_active
            else CONFIRM_OPEN_NEW_PROJECT
        )
        if system_console.confirm(confirm_message):
            close_subcommand(file_manager=file_manager)

    file_manager.load_folder(path=path_to_open)
    change_directory(path_to_open)

    formatted_path = get_relative_path(path_to_open)
    system_console.notification(formatted_path)


def close_subcommand(*args, **kwargs):
    """"""
    file_manager: FileManager = kwargs.get("file_manager")
    file_manager.close_folder()
