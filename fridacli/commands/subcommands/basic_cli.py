from fridacli.chatfiles.file_manager import FileManager
from fridacli.chatfiles.path_utilities import (
    change_directory,
    check_valid_dir,
    get_current_dir,
    get_home_path,
    get_sorted_file_list,
)
from fridacli.config.env_vars import BOT_NAME
from fridacli.commands.subcommands.subcommands_info import get_commands_df
from fridacli.predefined_phrases.chat_command import (
    ERROR_PATH_DOES_NOT_EXIST,
    PWD_COMMAND_OUTPUT,
)
from fridacli.interface.styles import (
    file_list_with_styles,
    format_to_columns,
    format_to_table,
)

from fridacli.common import (
    system_console
)

from fridacli.logger import Logger

logger = Logger()


def ls_subcommand(*args, **kwargs) -> None:
    """"""
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
    project_path = get_current_dir()
    system_console.notification(PWD_COMMAND_OUTPUT(project_path), bottom=0)
    pass


def cd_subcommand(*args, **kwargs) -> None:
    """"""
    directory_to_move = args[0] if args else get_home_path()
    logger.info(__name__, f"Help command cd: {directory_to_move}")
    valid_path = check_valid_dir(directory_to_move)
    if not valid_path:
        system_console.notification(
            ERROR_PATH_DOES_NOT_EXIST(directory_to_move), bottom=0
        )
        return
    change_directory(directory_to_move)


def help_subcommand(*args, **kwargs) -> None:
    """"""
    logger.info(__name__, "Help command open")
    subcommands_df = get_commands_df()
    table_output = format_to_table(
        subcommands_df, box=None, padding=True, expand=True, ratio=[1, 3, 1]
    )
    system_console.print(table_output, top=0, bottom=0, alignment="center")


def exit_subcommand(*args, **kwargs) -> None:
    """"""
    system_console.notification(f"{BOT_NAME}CLI Chat session ended")
    exit()
