from InquirerPy import inquirer
from InquirerPy.utils import InquirerPyStyle
from prompt_toolkit.completion.base import Completer
from rich.console import Console as RichConsole
from rich.padding import Padding
from rich.theme import Theme

from typing import Dict, Optional, Union

from fridacli.interface.styles import print_padding
from fridacli.interface.theme import (
    console_theme,
    user_input_style,
    user_input_style_active_project,
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
