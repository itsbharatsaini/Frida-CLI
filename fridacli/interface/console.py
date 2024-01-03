from rich.console import Console as RichConsole
from rich.padding import Padding
from rich.panel import Panel
from rich.theme import Theme
from rich.markdown import Markdown

import time

from fridacli.chatbot.predefined_phrases import INTERRUPT_CHAT, WELCOME_PANEL_MESSAGE
from fridacli.config.env_vars import BOT_NAME
from fridacli.interface.styles import add_styletags_to_string
from fridacli.interface.theme import console_theme


class Console:
    """A wrapper class for the Rich Console class that provides additional features and simplifies usage"""

    def __init__(self, theme: Theme = console_theme) -> None:
        self.__console = RichConsole(theme=theme)
        self.__codeblock = ""
        self.__in_codeblock = False

    def get_codeblock(self) -> str:
        return self.__codeblock

    def get_in_codeblock(self) -> bool:
        return self.__in_codeblock

    def set_codeblock(self, codeblock: str) -> None:
        self.__codeblock = codeblock

    def set_in_codeblock(self, in_codeblock: bool) -> None:
        self.__in_codeblock = in_codeblock

    def print(
        self,
        message: str,
        style: str = "system",
        alignment: str = "left",
        top: int = 1,
        bottom: int = 1,
        left: int = 0,
        right: int = 0,
        streaming: bool = False,
    ) -> None:
        """Prints a message to the console applying a style, a padding, an alignment and an end"""
        self.__console.print(
            Padding(message, (top, left, bottom, right)),
            style=style,
            justify=alignment,
            end="" if streaming else "\n",
        )

    def input(
        self,
        message: str = "",
        prefix: str = "",
        style: str = "system",
        top: int = 0,
        bottom: int = 0,
    ) -> str:
        """Prompts the user for input and returns the user's response."""
        if top > 0:
            print("\n" * (top - 1))
        formatted_input = f"{(prefix + ':') if prefix else ''}{message}"
        self.__console.print(formatted_input, style=style, end=" ")
        user_response = input()
        if bottom > 0:
            print("\n" * (bottom - 1))
        return user_response

    def confirm(
        self,
        message: str,
        style: str = "system",
        top: int = 1,
        bottom: int = 0,
        warning: bool = False,
    ) -> bool:
        """Asks the user for confirmation and returns `True` if the user confirms, `False` otherwise."""
        confirm_options = {"accept": ("y", "yes", ""), "reject": ("n", "no")}
        valid_inputs = add_styletags_to_string(
            "\[y/n]", style="error" if warning else "option"
        )

        formatted_input = f"{message} {valid_inputs}"
        user_response = self.input(
            message=formatted_input, top=top, bottom=bottom
        ).lower()

        if user_response in confirm_options["accept"]:
            return True
        elif user_response in confirm_options["reject"]:
            print()
            return False
        else:
            return self.confirm(message, style=style, warning=True)

    def notification(self, message: str) -> None:
        """Display a notification message centered and gray in text color."""
        self.print(
            message,
            style="system",
            alignment="center",
        )

    def print_panel(
        self,
        message: str = WELCOME_PANEL_MESSAGE,
        title: str = "FRIDA CLI",
        subtitle: str = INTERRUPT_CHAT,
    ) -> None:
        """Displays a stylized rich panel with a message, a title and a subtitle."""
        self.print(
            Panel(message, title=title, subtitle=subtitle, padding=(1, 2)),
            left=10,
            right=10,
        )

    def response(
        self,
        message: str,
        prefix: str = BOT_NAME,
        style: str = "bot",
        top: int = 1,
        bottom: int = 1,
        streaming: bool = True,
    ) -> None:
        """Print a formatted response."""

        def append_to_codeblock(character):
            """Append a character to the current codeblock."""
            self.set_codeblock(self.get_codeblock() + character)

        def toggle_in_codeblock(character):
            """Toggle codeblock mode."""
            self.set_in_codeblock(not self.get_in_codeblock())
            self.set_codeblock(self.get_codeblock() + character)

            if not self.get_in_codeblock():
                process_end_of_codeblock()

        def process_end_of_codeblock():
            """Process the end of a codeblock."""
            codeblock = self.get_codeblock()
            codeblock_with_content = len(codeblock.replace("`", "")) > 0

            if codeblock_with_content:
                backticks = codeblock.count("`")
                inline_format = backticks == 2
                block_format = backticks == 6

                if block_format:
                    self.print(Markdown(codeblock), bottom=0)
                    self.set_codeblock("")

                elif inline_format:
                    formatted_inline_code = codeblock[1:-1]
                    self.__console.print(formatted_inline_code, style="code", end="")
                    self.set_codeblock("")

        def process_character(character):
            """Process each character in streaming mode."""
            if character == "`":
                toggle_in_codeblock(character)

            elif self.get_in_codeblock():
                append_to_codeblock(character)

            else:
                self.__console.print(character, style=style, end="")
                time.sleep(0.04)

        if streaming:
            if top > 0:
                print("\n" * (top - 1))

            self.__console.print(f"{prefix}:", style=style, end=" ")

            for character in message:
                process_character(character)

            if bottom > 0:
                print("\n" * bottom)
        else:
            formatted_output = f"{(prefix + ':') if prefix else ''} {message}"
            self.print(Markdown(formatted_output), style=style)
