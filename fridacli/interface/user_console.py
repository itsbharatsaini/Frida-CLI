from prompt_toolkit.completion.base import Completer

from typing import Dict, Optional, Union

from fridacli.interface.console import Console
from fridacli.interface.theme import (
    user_input_style,
    user_input_style_active_project,
)


class UserConsole(Console):
    """"""

    def __init__(self, username: str):
        self.username = username

    def user_input(
        self,
        current_dir: str,
        open_folder: bool,
        completer: Optional[Union[Dict[str, Optional[str]], "Completer"]] = None,
    ) -> str:
        """Wrapper function for the input method that provides
        a stylized input with the user information."""
        style = user_input_style_active_project if open_folder else user_input_style
        return self.input(
            prefix=f"({current_dir})",
            message=self.username,
            style=style,
            completer=completer,
        )
