from pandas import DataFrame

from fridacli.interface.styles import add_styletags_from_regex


SUBCOMMANDS_INFO = {
    "!exit": {
        "description": "Exit the chat",
        "usage": "!exit",
    },
    "!help": {
        "description": "List available commands",
        "usage": "!help",
    },
    "!pwd": {
        "description": "Shows the current directory",
        "usage": "!pwd",
    },
    "!ls": {
        "description": "List or display the contents of a directory",
        "usage": "!ls",
    },
    "!cd": {
        "description": "Move to a specified directory",
        "usage": "!cd",
    },
}


def get_commands_df() -> DataFrame:
    """"""
    df_rows = {"Command": [], "Description": [], "Usage": []}

    for command, info in SUBCOMMANDS_INFO.items():
        # Applies styles to command information
        command_name = add_styletags_from_regex(command)
        command_description = add_styletags_from_regex(info["description"])
        command_usage = add_styletags_from_regex(info["usage"])

        # Add formatted info to Dataframe rows
        df_rows["Command"].append(command_name)
        df_rows["Description"].append(command_description)
        df_rows["Usage"].append(command_usage)

    return DataFrame(df_rows)
