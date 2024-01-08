import os

from fridacli.chatbot.predefined_phrases import (
    CONFIGFILE_OVERWRITE,
    ERROR_MISSING_CONFIGFILE,
    message_config_file_path,
    success_configfile_create,
    success_configfile_update,
)
from fridacli.config.env_vars import config_file_exists, config_file_path, HOME_PATH
from fridacli.interface.system_console import SystemConsole
from fridacli.interface.styles import format_path


system = SystemConsole()


# ========= frida config --list =========


def read_config_file(path: str = config_file_path) -> str:
    """Read the contents of a configuration file and returns it."""
    with open(path, "r") as file_content:
        configfile_content = file_content.read()
    return configfile_content.rstrip("\n")


def print_config_list() -> None:
    """Print the contents of the configuration file."""
    if config_file_exists():
        formatted_config_file_path = format_path(config_file_path, HOME_PATH)
        config_output = message_config_file_path(formatted_config_file_path)
        config_output += "\n" + read_config_file()
        system.print(config_output)
    else:
        system.notification(ERROR_MISSING_CONFIGFILE)


# ========= frida config =========


def write_config_to_file(api_key: str, path: str = config_file_path) -> None:
    """Write the configuration file with the API key."""
    config_input = f"LLMOPS_FRIDACLI_API_KEY={api_key}"
    command = f"echo {config_input} > {path}"
    os.system(command)


def configurate_api_keys() -> None:
    """Configure the API keys and write them to the configuration file."""
    new_configfile = not config_file_exists()
    if not new_configfile:
        overwrite = system.confirm(CONFIGFILE_OVERWRITE)
        if not overwrite:
            return

    api_key = system.password("Enter your Softtek SKD API key", top=1)
    write_config_to_file(api_key)

    formatted_path = format_path(config_file_path, HOME_PATH)
    success_message = (
        success_configfile_create(formatted_path)
        if new_configfile
        else success_configfile_update(formatted_path)
    )
    system.notification(success_message)


# ========= config command =========


def exec_config(list_option: bool) -> None:
    """Execute the configuration command."""
    if list_option:
        print_config_list()
    else:
        configurate_api_keys()
