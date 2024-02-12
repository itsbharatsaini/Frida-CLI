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
from fridacli.interface.styles import print_padding
from fridacli.interface.user_console import UserConsole

from .predefined_phrases import (
    execution_result,
    LANG_NOT_FOUND,
    RUN_CONFIRMATION_MESSAGE,
    WRITE_CONFIRMATION_MESSAGE,
)
from fridacli.fridaCoder.exceptionMessage import ExceptionMessage
from fridacli.common import (
    system_console,
    file_manager,
    chatbot_agent,
    chatbot_console,
    frida_coder,
)


def start_panel() -> None:
    """"""
    system_console.print_panel(
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
        system_console.notification(ERROR_INVALID_COMMAND(subcommand))
    else:
        SUBCOMMANDS_CALLBACKS[subcommand]["execute"](*args)
        print_padding()


def chat_session() -> None:
    """"""
    chatting = True
    user = UserConsole(username=get_username())

    start_panel()

    while chatting:
        try:
            current_dir = os.path.basename(os.getcwd())
            completions = get_completions()
            user_input = user.user_input(
                current_dir=current_dir,
                completer=completions,
                open_folder=file_manager.get_folder_status(),
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
                response = chatbot_agent.chat(user_input, False)
                # Chatbot response from the user input
                chatbot_console.response(response, streaming=True)

                # Get the code block in the chat response if any
                code_blocks = frida_coder.prepare(response)
                if len(code_blocks) > 0:
                    # Go code block by code block
                    for code_block in code_blocks:
                        # Check if in the prompt has files used, and if so ask to overwrite
                        """
                        TODO:
                            Add a way to check if the code is the same
                        """
                        if chatbot_agent.is_files_open():
                            write_confirmation = system_console.confirm(
                                WRITE_CONFIRMATION_MESSAGE
                            )
                            if write_confirmation:
                                first_file_required = list(
                                    chatbot_agent.get_files_required()
                                )[0]
                                path = file_manager.get_file_path(first_file_required)
                                frida_coder.write_code_to_path(path, code_block["code"])
                        # Ask for confirmation to run the code
                        run_confirmation = system_console.confirm(RUN_CONFIRMATION_MESSAGE)
                        if run_confirmation:
                            code_result = frida_coder.run(
                                code_block, list(chatbot_agent.get_files_required())
                            )
                            # If errors are detected in the code, prompt for confirmation before submitting feedback to the chat bot
                            if code_result["status"] == ExceptionMessage.RESULT_ERROR:
                                chat_execution_response = execution_result(code_result)
                                chatbot_console.response(
                                    chat_execution_response, streaming=True
                                )
                                """
                                TODO:
                                    Confirm if the user wants to ask the agent
                                error_confirm = system.confirm(ERROR_CONFIRMATION_MESSAGE)
                                if error_confirm:
                                    error_correction_result = chatbot_agent.chat(
                                        error_chat_prompt(
                                            response["code"], response["result"]
                                        )
                                    )
                                    chatbot_console.response(error_correction_result, streaming=True)
                                """
                            # If the is no errors show the result of the execution
                            elif (
                                code_result["status"]
                                == ExceptionMessage.GET_RESULT_SUCCESS
                            ):
                                if (
                                    "result" in code_result
                                    or len(code_result["result"]) > 0
                                ):
                                    chat_execution_response = execution_result(
                                        code_result
                                    )
                                    chatbot_console.response(
                                        chat_execution_response, streaming=True
                                    )
                                    frida_coder.clean()
                            # If an unknown code language is detected
                            else:
                                chatbot_console.response(LANG_NOT_FOUND, streaming=True)

        except KeyboardInterrupt:
            exec_subcommand("!exit")


def exec_chat(path: str | None, tokens: bool):
    """"""
    if not config_file_exists():
        system_console.notification(ERROR_MISSING_CONFIGFILE)
        return

    system_console.print("Initializing...", style="process", bottom=0)

    chat_session()
