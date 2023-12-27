import os

from fridacli.chatbot.predefined_phrases import (
    CONFIGFILE_OVERWRITE,
    ERROR_MISSING_CONFIGFILE,
    success_configfile_create,
    success_configfile_update,
)
from fridacli.config.env_vars import configfile_path
from fridacli.interface.console import Console
from fridacli.interface.styles import add_styletags_to_string

console = Console()


def print_config_list() -> None:
    """Print the contents of the configuration file."""
    if os.path.exists(configfile_path):
        config_output = (
            "Configuration file path: "
            + f"{add_styletags_to_string(configfile_path,style='path')}\n"
        )
        with open(configfile_path, "r") as file_content:
            config_output += file_content.read()
        console.print(config_output, bottom=0)
    else:
        console.print(ERROR_MISSING_CONFIGFILE, alignment="center")


def configurate_api_keys() -> None:
    """Configure the API keys and write them to the configuration file."""
    new_configfile = not os.path.exists(configfile_path)
    if not new_configfile:
        if not console.confirm(CONFIGFILE_OVERWRITE):
            return

    api_key = console.input("Enter your Softtek SKD API key:", top=1)
    config_input = f"LLMOPS_FRIDACLI_API_KEY={api_key}"
    command = f"echo {config_input} > {configfile_path}"
    os.system(command)

    success_message = (
        success_configfile_create(configfile_path)
        if new_configfile
        else success_configfile_update(configfile_path)
    )
    console.print(
        success_message,
        style="system",
        alignment="center",
    )


def exec_config(list_option: bool) -> None:
    """Execute the configuration command."""
    if list_option:
        print_config_list()
    else:
        configurate_api_keys()
