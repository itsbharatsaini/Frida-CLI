from fridacli.interface.system_console import SystemConsole
from fridacli.config.env_vars import BOT_NAME


def ls_subcommand(*args, **kwargs):
    """"""
    pass


def pwd_subcommand(*args, **kwargs):
    """"""
    pass


def cd_subcommand(*args, **kwargs):
    """"""
    pass


def help_subcommand(*args, **kwargs):
    """"""
    pass


def exit_subcommand(*args, **kwargs) -> None:
    """"""
    system_console: SystemConsole = kwargs["system_console"]
    system_console.notification(f"{BOT_NAME}CLI Chat session ended")
    exit()
