import os

from fridacli.chatbot.predefined_phrases import (
    ERROR_MISSING_CONFIGFILE,
    ERROR_INVALID_COMMAND,
    INTERRUPT_CHAT,
    WELCOME_PANEL_MESSAGE,
)
from fridacli.config.env_vars import config_file_exists, get_config_vars, get_username
from fridacli.commands.subcommands.callbacks import (
    get_completions,
    SUBCOMMANDS_CALLBACKS,
)
from fridacli.interface.bot_console import BotConsole
from fridacli.interface.styles import print_padding
from fridacli.interface.system_console import SystemConsole
from fridacli.interface.user_console import UserConsole


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


def exec_subcommand(subcommand: str, *args):
    """"""
    if subcommand not in SUBCOMMANDS_CALLBACKS:
        system.notification(ERROR_INVALID_COMMAND(subcommand))
    else:
        SUBCOMMANDS_CALLBACKS[subcommand]["execute"](*args, system_console=system)


def chat_session() -> None:
    """"""
    chatting = True
    user = UserConsole(username=get_username())
    chatbot = BotConsole()
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
                response_test = (
                    "Bot Response.\n"
                    + "```python\nprint('Hello world')\n"
                    + "```\nHola `mundo` ;D"
                )
                chatbot.response(response_test, streaming=True)

        except KeyboardInterrupt:
            exec_subcommand("!exit")


def exec_chat(path: str | None, tokens: bool):
    """"""
    if not config_file_exists():
        system.notification(ERROR_MISSING_CONFIGFILE)
        return

    system.print("Initializing...", style="process", bottom=0)

    env_vars = get_config_vars()
    api_key = env_vars["LLMOPS_FRIDACLI_API_KEY"]

    chat_session()
