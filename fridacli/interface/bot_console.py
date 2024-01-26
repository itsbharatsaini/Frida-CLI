import os
import re
import time
import datetime
from rich.markdown import Markdown
from fridacli.config.env_vars import BOT_NAME
from fridacli.interface.console import Console
from fridacli.interface.styles import print_padding


class BotConsole(Console):
    """
    Check if the bot respose has code included
    """

    def __init__(self):
        super().__init__()
        self.__codeblock = ""
        self.__in_codeblock = False
        self.code_files_dir = "tmp/"

    def get_codeblock(self) -> str:
        return self.__codeblock

    def get_in_codeblock(self) -> bool:
        return self.__in_codeblock

    def set_codeblock(self, codeblock: str) -> None:
        self.__codeblock = codeblock

    def set_in_codeblock(self, in_codeblock: bool) -> None:
        self.__in_codeblock = in_codeblock

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
                    self._console.print(formatted_inline_code, style="code", end="")
                    self.set_codeblock("")

        def process_character(character):
            """Process each character in streaming mode."""
            if character == "`":
                toggle_in_codeblock(character)

            elif self.get_in_codeblock():
                append_to_codeblock(character)

            else:
                self._console.print(character, style=style, end="")
                time.sleep(0.02)

        if streaming:
            print_padding(padding=top)
            self._console.print(f"{prefix}:", style=style, end=" ")
            for character in message:
                process_character(character)
            print_padding(padding=(bottom + 1))
        else:
            formatted_output = f"{(prefix + ':') if prefix else ''} {message}"
            self.print(Markdown(formatted_output), style=style)
