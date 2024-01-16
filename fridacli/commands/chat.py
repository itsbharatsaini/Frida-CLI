import os
from typing import Dict

from fridacli.chatbot.predefined_phrases import (
    ERROR_MISSING_CONFIGFILE,
    INTERRUPT_CHAT,
    WELCOME_PANEL_MESSAGE,
)
from fridacli.config.env_vars import config_file_exists, get_config_vars, get_username
from fridacli.commands.chat_subcommands import SUBCOMMANDS
from fridacli.interface.bot_console import BotConsole
from fridacli.interface.styles import print_padding
from fridacli.interface.system_console import SystemConsole
from fridacli.interface.user_console import UserConsole

from chatbot.chatbot import ChatbotAgent

system = SystemConsole()


def start_panel() -> None:
    """"""
    system.print_panel(
        message=WELCOME_PANEL_MESSAGE, title="FRIDA CLI", subtitle=INTERRUPT_CHAT
    )


def get_command_parts(command_string: str) -> tuple[str, list[str]]:
    """"""
    words = command_string.split(" ")
    command = words[0]
    command_args = words[1:] if len(words) > 1 else []
    return command, command_args


def get_completions() -> Dict:
    """"""
    completions = {
        subcommand: command_info["completions"]
        for subcommand, command_info in SUBCOMMANDS.items()
        if "completions" in command_info
    }
    return completions


def exec_subcommand(subcommand: str, *args):
    """"""
    if subcommand not in SUBCOMMANDS:
        system.notification("ERROR")
    else:
        SUBCOMMANDS[subcommand]["execute"](*args)


def chat_session() -> None:
    """"""
    chatting = True
    user = UserConsole(username=get_username())
    chatbot_console = BotConsole()
    chatbot_agent = ChatbotAgent()

    start_panel()

    while chatting:
        try:
            current_dir = os.path.basename(os.getcwd())
            completions = get_completions()
            user_input = user.user_input(
                current_dir=current_dir, completer=completions, open_folder=False
            )
            is_empty = len(user_input.replace(" ", "")) == 0
            is_command = user_input.startswith("!")

            # If it's an empty input
            if is_empty:
                print_padding()
                continue

            # If the input is a command
            if is_command:
                command, command_args = get_command_parts(user_input)
                exec_subcommand(command, *command_args)

            else:
                response = chatbot_agent.chat(user_input)
                chatbot_console.response(response, streaming=True)
                

        except KeyboardInterrupt:
            exec_subcommand("!exit")


def exec_chat(path: str | None, tokens: bool):
    """"""
    if not config_file_exists():
        system.notification(ERROR_MISSING_CONFIGFILE)
        return

    system.print("Initializing...", style="process", bottom=0)

    chat_session()
