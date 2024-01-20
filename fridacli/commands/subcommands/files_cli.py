from fridacli.chatfiles.file_manager import FileManager
from fridacli.chatfiles.path_utilities import (
    check_samepath,
    change_directory,
    get_relative_path,
    get_current_dir,
)
from fridacli.interface.system_console import SystemConsole


def open_subcommand(*args, **kwargs):
    """"""
    system_console: SystemConsole = kwargs.get("system_console")
    file_manager: FileManager = kwargs.get("file_manager")

    if not args:
        system_console.notification("Argument required")
        return

    path_to_open = args[0]
    formatted_path = get_relative_path(path_to_open)
    active_folder = file_manager.get_folder_status()
    current_folder_active = check_samepath(get_current_dir(), path_to_open)

    if active_folder and current_folder_active:
        system_console.notification("Directory already open")
        return

    if active_folder and system_console.confirm("Wanna close current project?"):
        close_subcommand(file_manager=file_manager)

    file_manager.load_folder(path=path_to_open)
    change_directory(path_to_open)
    system_console.notification(formatted_path)


def close_subcommand(*args, **kwargs):
    """"""
    file_manager: FileManager = kwargs.get("file_manager")
    file_manager.close_folder()
