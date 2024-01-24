from InquirerPy import inquirer
from InquirerPy.utils import InquirerPyStyle
from rich.panel import Panel

from fridacli.interface.console import Console
from fridacli.interface.styles import print_padding
from fridacli.interface.theme import basic_style



class SystemConsole(Console):
    """"""

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
        print_padding(padding=bottom)
        return confirm

    def notification(self, message: str, top: int = 1, bottom: int = 1) -> None:
        """Display a notification message centered and gray in text color."""
        self.print(
            message, 
            style="system", 
            alignment="center", 
            top=top, 
            bottom=bottom
        )
        
    def steps_notification(self, message: str) -> None:
        self.print(
            message,
            style="system",
            right=1,
            top=0,
            bottom=0
        )
        
    def print_panel(
        self,
        message: str,
        title: str,
        subtitle: str,
    ) -> None:
        """Displays a stylized rich panel with a message, a title and a subtitle."""
        self.print(
            Panel(message, title=title, subtitle=subtitle, padding=(1, 2)),
            left=10,
            right=10,
        )
