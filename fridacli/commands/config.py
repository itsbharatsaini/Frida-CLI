import os

from fridacli.chatbot.predefined_phrases import (
    CONFIGFILE_OVERWRITE,
    ERROR_MISSING_CONFIGFILE,
    message_config_file_path,
    success_configfile_create,
    success_configfile_update,
)
from fridacli.config.env_vars import config_file_exists, config_file_path
from fridacli.interface.console import Console


console = Console()


# ========= frida config --list =========


def read_config_file(path: str = config_file_path) -> str:
    """Read the contents of a configuration file and returns it."""
    with open(path, "r") as file_content:
        configfile_content = file_content.read()
    return configfile_content.rstrip("\n")


def print_config_list() -> None:
    """Print the contents of the configuration file."""
    if config_file_exists():
        config_output = message_config_file_path(config_file_path)
        config_output += "\n" + read_config_file()
        console.print(config_output)
    else:
        console.notification(ERROR_MISSING_CONFIGFILE)


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
        overwrite = console.confirm(CONFIGFILE_OVERWRITE)
        if not overwrite:
            return

    api_key = console.input("Enter your Softtek SKD API key:", top=1)
    write_config_to_file(api_key)

    success_message = (
        success_configfile_create(config_file_path)
        if new_configfile
        else success_configfile_update(config_file_path)
    )
    console.notification(success_message)


# ========= config command =========


def exec_config(list_option: bool) -> None:
    """Execute the configuration command."""
    if list_option:
        print_config_list()
    else:
        configurate_api_keys()
