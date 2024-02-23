import typer

from typing import Optional
from typing_extensions import Annotated

from fridacli.commands.config import exec_config
from fridacli.logger import Logger
logger = Logger()


frida_cli = typer.Typer()


@frida_cli.command()
def chat(
    path: Annotated[Optional[str], typer.Argument()] = None,
    tokens: Optional[bool] = False,
):
    """Command to chat with FridaCLI AI assistant."""
    logger.info(__name__, "Chat funtion selected")
    from fridacli.commands.chat import exec_chat
    exec_chat(path=path, tokens=tokens)


@frida_cli.command()
def config(list: Optional[bool] = False, pythonenv: Optional[bool] = False):
    """Command to list or configure API keys."""
    logger.info(__name__, f"Config funtion selected, list_option={list} python_env={pythonenv}")
    exec_config(list_option=list, python_env=pythonenv)


if __name__ == "__main__":
    frida_cli()
