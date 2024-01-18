from fridacli.commands.subcommands.basic_cli import exit_subcommand, pwd_subcommand
from fridacli.commands.subcommands.recipes_cli import angular_voyager 

SUBCOMMANDS = {
    "!exit": {
        "description": "Exit the chat",
        "usage": "!exit",
        "completions": None,
        "execute": exit_subcommand,
    },
    "!pwd": {
        "description": "Shows the current directory",
        "usage": "!pwd",
        "completions": None,
        "execute": pwd_subcommand,
    },
    "!angular_voyager": {
        "description": "Upgrade an Angular project from an older version to the latest release",
        "usage": "!angular_voyager",
        "completions": None,
        "execute": angular_voyager,
    },
}
