from fridacli.chatfiles.path_utilities import (
    change_directory,
    check_valid_dir,
    get_current_dir,
    get_home_path,
    get_sorted_file_list,
)
from fridacli.config.env_vars import BOT_NAME
from fridacli.commands.subcommands.subcommands_info import get_commands_df
from fridacli.commands.subcommands.predefined_phrases import ERROR_PATH_DOES_NOT_EXIST
from fridacli.interface.system_console import SystemConsole
from fridacli.interface.styles import (
    file_list_with_styles,
    format_to_columns,
    format_to_table,
)


def ls_subcommand(*args, **kwargs) -> None:
    """"""
    system_console: SystemConsole = kwargs.get("system_console")
    root = args[0] if args else get_current_dir()
    valid_path = check_valid_dir(root)
    if not valid_path:
        system_console.notification(ERROR_PATH_DOES_NOT_EXIST(root))
        return
    file_list = file_list_with_styles(get_sorted_file_list(root))
    columns_output = format_to_columns(file_list)
    system_console.print(columns_output, bottom=0)


def pwd_subcommand(*args, **kwargs):
    """"""
    pass


def cd_subcommand(*args, **kwargs) -> None:
    """"""
    system_console: SystemConsole = kwargs.get("system_console")
    directory_to_move = args[0] if args else get_home_path()
    valid_path = check_valid_dir(directory_to_move)
    if not valid_path:
        system_console.notification(ERROR_PATH_DOES_NOT_EXIST(directory_to_move))
        return
    change_directory(directory_to_move)


def help_subcommand(*args, **kwargs) -> None:
    """"""
    subcommands_df = get_commands_df()
    table_output = format_to_table(
        subcommands_df, box=None, padding=True, expand=True, ratio=[1, 3, 1]
    )
    system_console: SystemConsole = kwargs.get("system_console")
    system_console.print(table_output, top=0, bottom=0, alignment="center")


def exit_subcommand(*args, **kwargs) -> None:
    """"""
    system_console: SystemConsole = kwargs.get("system_console")
    system_console.notification(f"{BOT_NAME}CLI Chat session ended")
    exit()
