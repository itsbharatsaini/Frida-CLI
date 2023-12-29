import typer

from typing import Optional
from typing_extensions import Annotated

from fridacli.commands.chat import exec_chat
from fridacli.commands.config import exec_config


frida_cli = typer.Typer()


@frida_cli.command()
def chat(
    path: Annotated[Optional[str], typer.Argument()] = None,
    tokens: Optional[bool] = False,
):
    """Command to chat with FridaCLI AI assistant."""
    exec_chat(path=path, tokens=tokens)


@frida_cli.command()
def config(list: Optional[bool] = False):
    """Command to list or configure API keys."""
    exec_config(list_option=list)


if __name__ == "__main__":
    frida_cli()
