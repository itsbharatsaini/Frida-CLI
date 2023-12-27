from rich.theme import Theme
from rich.console import Console as RichConsole
from rich.padding import Padding

from fridacli.interface.theme import console_theme
from fridacli.interface.styles import add_styletags_to_string


class Console:
    """"""

    def __init__(self, theme: Theme = console_theme) -> None:
        self.__console = RichConsole(theme=theme)

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
        """"""
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
        """"""
        if top > 0:
            print("\n" * (top - 1))
        formatted_input = f"{(prefix + ': ') if prefix else ''}{message}"
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
        """"""
        confirm_options = {"accept": ("y", "yes", ""), "reject": ("n", "no")}
        valid_inputs = add_styletags_to_string(
            "\[y/n]", style="error" if warning else "option"
        )

        formatted_input = f"{message} {valid_inputs}"
        user_response = self.input(
            message=formatted_input, top=top, bottom=bottom
        ).lower()

        if user_response in confirm_options["reject"]:
            print()

        return (
            True
            if user_response in confirm_options["accept"]
            else False
            if user_response in confirm_options["reject"]
            else self.confirm(message, style=style, warning=True)
        )
