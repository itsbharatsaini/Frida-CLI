import os
from fridacli.config.env_vars import configfile_path
from fridacli.interface.styles import add_styletags_to_string
from fridacli.chatbot.predefined_phrases import (
    ERROR_MISSING_CONFIGFILE,
    success_configfile_create,
    success_configfile_update,
)


def print_config_list() -> None:
    """Print the contents of the configuration file."""
    if os.path.exists(configfile_path):
        config_output = (
            "Configuration file path: "
            + f"{add_styletags_to_string(configfile_path,style='path')}\n"
        )
        with open(configfile_path, "r") as file_content:
            config_output += file_content.read()
        print(config_output)
    else:
        print(ERROR_MISSING_CONFIGFILE)


def configurate_api_keys() -> None:
    """Configure the API keys and write them to the configuration file."""
    new_configfile = not os.path.exists(configfile_path)
    api_key = input("Enter your Softtek SKD API key: ")
    config_input = f"LLMOPS_FRIDACLI_API_KEY={api_key}"
    command = f"echo {config_input} > {configfile_path}"
    os.system(command)
    print(
        success_configfile_create(configfile_path)
        if new_configfile
        else success_configfile_update(configfile_path)
    )


def exec_config(list_option: bool) -> None:
    """Execute the configuration command."""
    if list_option:
        print_config_list()
    else:
        configurate_api_keys()
