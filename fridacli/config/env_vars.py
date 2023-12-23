import os
from typing import Dict
from fridacli.interface.styles import add_styletags_to_string


def get_config_vars(path: str) -> Dict:
    """"""
    config_variables = {}
    with open(path, "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            config_variables[key] = value
    return config_variables


# Config env variables
configfile_path = f"{os.environ.get('HOME')}/.fridacli"

# Chatbot env variables
BOT_NAME = "Frida"
INTERRUPT_CHAT = f"Press {add_styletags_to_string('Ctrl+C','operation')} (keyboard interrupt) to exit the chat"
WELCOME_SUBTITLE = add_styletags_to_string(
    "This is your personal "
    + add_styletags_to_string(f"{BOT_NAME} AI assistant", "bot")
    + ", you can ask any coding related question directly in the command line or type "
    + add_styletags_to_string("!help", "command")
    + " to see the available commands.",
    style="info",
)
