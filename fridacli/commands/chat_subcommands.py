from fridacli.commands.subcommands.basic_cli import exit_subcommand, pwd_subcommand

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
}
