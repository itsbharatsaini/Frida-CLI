from chatbot.predefined_phrases import ERROR_MISSING_CONFIGFILE
from config.env_vars import config_file_exists, get_config_vars, get_username
from interface.console import Console


console = Console()


def get_command_parts(command_string: str):
    """"""
    words = command_string.split(" ")
    command = words[0]
    command_args = words[1:] if len(words) > 1 else []
    return command, command_args


def chat_session(username: str) -> None:
    """"""
    chatting = True
    console.print_panel()
    while chatting:
        try:
            user_input = console.input(prefix=username, style="user")
            is_empty = len(user_input.replace(" ", "")) == 0
            is_command = user_input.startswith("!")

            # If it's an empty input
            if is_empty:
                print()
                continue

            # If the input is a command
            if is_command:
                command, command_args = get_command_parts(user_input)

            else:
                response_test = (
                    "Bot Response.\n"
                    + "```python\nprint('Hello world')\n"
                    + "```\nHola `mundo` ;D"
                )
                console.response(response_test, streaming=True)

        except KeyboardInterrupt:
            print()
            exit()


def exec_chat(path: str | None, tokens: bool):
    """"""
    if not config_file_exists():
        console.notification(ERROR_MISSING_CONFIGFILE)
        return

    console.print("Initializing...", style="process", bottom=0)

    env_vars = get_config_vars()
    api_key = env_vars["LLMOPS_FRIDACLI_API_KEY"]
    username = get_username()

    chat_session(username=username)
