import os

from fridacli.chatfiles.file_manager import FileManager
from fridacli.interface.system_console import SystemConsole


def open_subcommand(*args, **kwargs):
    """"""
    system_console: SystemConsole = kwargs["system_console"]
    file_manager: FileManager = kwargs["file_manager"]

    active_folder = file_manager.get_folder_status()
    if active_folder and system_console.confirm("Wanna close?"):
        close_subcommand(file_manager=file_manager)

    path = args[0] if args else os.getcwd()
    file_manager.load_folder(path=path)
    system_console.notification(path)


def close_subcommand(*args, **kwargs):
    """"""
    file_manager: FileManager = kwargs["file_manager"]
    file_manager.close_folder()
