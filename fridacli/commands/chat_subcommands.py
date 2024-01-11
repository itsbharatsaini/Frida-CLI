from fridacli.commands.subcommands.basic_cli import (
    exit_subcommand,
    help_subcommand,
    ls_subcommand,
    pwd_subcommand,
    cd_subcommand,
)

SUBCOMMANDS = {
    "!exit": {
        "description": "Exit the chat",
        "usage": "!exit",
        "completions": None,
        "execute": exit_subcommand,
    },
    "!help": {
        "description": "List available commands",
        "usage": "!exit",
        "completions": None,
        "execute": help_subcommand,
    },
    "!pwd": {
        "description": "Shows the current directory",
        "usage": "!pwd",
        "completions": None,
        "execute": pwd_subcommand,
    },
    "!ls": {
        "description": "List or display the contents of a directory",
        "usage": "!ls",
        "completions": None,
        "execute": ls_subcommand,
    },
    "!cd": {
        "description": "Move to a specified directory",
        "usage": "!cd",
        "completions": None,
        "execute": cd_subcommand,
    },
}
