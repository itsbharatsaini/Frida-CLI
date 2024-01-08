from InquirerPy import inquirer
from InquirerPy.utils import InquirerPyStyle
from prompt_toolkit.completion.base import Completer
from rich.console import Console as RichConsole
from rich.padding import Padding
from rich.panel import Panel
from rich.theme import Theme

from typing import Dict, Optional, Union

from fridacli.chatbot.predefined_phrases import INTERRUPT_CHAT, WELCOME_PANEL_MESSAGE
from fridacli.interface.styles import print_padding
from fridacli.interface.theme import (
    console_theme,
    user_input_style,
    user_input_style_active_project,
    basic_style,
)


class Console:
    """A wrapper class for the Rich Console class that provides additional features and simplifies usage"""

    def __init__(self, theme: Theme = console_theme) -> None:
        self._console = RichConsole(theme=theme)

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
        self._console.print(
            Padding(message, (top, left, bottom, right)),
            style=style,
            justify=alignment,
            end="" if streaming else "\n",
        )

    def input(
        self,
        message: str = "",
        style: InquirerPyStyle = None,
        completer: Optional[Union[Dict[str, Optional[str]], "Completer"]] = None,
        prefix: str = "",
        top: int = 0,
        bottom: int = 0,
    ) -> str:
        """Prompts the user for input and returns the user's response."""
        print_padding(padding=top)
        user_response = inquirer.text(
            message=f"{message}:",
            style=style,
            completer=completer,
            qmark=prefix,
            amark=prefix,
        ).execute()
        print_padding(padding=bottom)
        return str(user_response)

    def password(
        self,
        message: str = "",
        style: InquirerPyStyle = basic_style,
        prefix: str = "",
        top: int = 0,
        bottom: int = 0,
    ) -> str:
        """Returns an user input stylized in a password format like a string."""
        print_padding(padding=top)
        password = inquirer.secret(
            message=f"{message}:",
            style=style,
            qmark=prefix,
            amark=prefix,
        ).execute()
        print_padding(padding=bottom)
        return str(password)

    def confirm(
        self,
        message: str,
        style: InquirerPyStyle = basic_style,
        prefix: str = "",
        top: int = 1,
        bottom: int = 0,
    ) -> bool:
        """Asks the user for confirmation and returns `True` if the user confirms, `False` otherwise."""
        print_padding(padding=top)
        confirm: bool = inquirer.confirm(
            message=message,
            style=style,
            qmark=prefix,
            amark=prefix,
        ).execute()
        print_padding(padding=bottom + (1 if not confirm else 0))
        return confirm

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

    def user_input(
        self,
        username: str,
        current_dir: str,
        open_folder: bool,
        completer: Optional[Union[Dict[str, Optional[str]], "Completer"]] = None,
    ) -> str:
        """Wrapper function for the input method that provides
        a stylized input with the user information."""
        style = user_input_style_active_project if open_folder else user_input_style
        return self.input(
            prefix=f"({current_dir})",
            message=username,
            style=style,
            completer=completer,
        )
