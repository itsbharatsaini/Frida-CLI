from typing import Dict

from fridacli.commands.subcommands.basic_cli import (
    exit_subcommand,
    help_subcommand,
    ls_subcommand,
    pwd_subcommand,
    cd_subcommand,
)
from fridacli.commands.subcommands.files_cli import open_subcommand, close_subcommand
from fridacli.commands.subcommands.recipes_cli import (
    angular_voyager,
    asp_voyager,
    document,
)


SUBCOMMANDS_CALLBACKS = {
    "!exit": {
        "completions": None,
        "execute": exit_subcommand,
    },
    "!help": {
        "completions": None,
        "execute": help_subcommand,
    },
    "!pwd": {
        "completions": None,
        "execute": pwd_subcommand,
    },
    "!ls": {
        "completions": None,
        "execute": ls_subcommand,
    },
    "!cd": {
        "completions": None,
        "execute": cd_subcommand,
    },
    "!open": {
        "completions": None,
        "execute": open_subcommand,
    },
    "!close": {
        "completions": None,
        "execute": close_subcommand,
    },
    "!asp_voyager": {
        "completions": None,
        "execute": asp_voyager,
    },
    "!document": {
        "completions": None,
        "execute": document,
    },
}


def get_completions() -> Dict:
    """"""
    completions = {
        subcommand: command_info["completions"]
        for subcommand, command_info in SUBCOMMANDS_CALLBACKS.items()
        if "completions" in command_info
    }
    return completions
