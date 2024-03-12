from fridacli.gui.fridacli import FridaCLI
from fridacli.config import get_config_vars
from fridacli.commands.subcommands.files_commands import open_subcommand
"""
    TODO: Create a setup view to download the model for sentence transforme
"""
if __name__ == "__main__":
    keys = get_config_vars()
    open_subcommand(keys["PROJECT_PATH"])
    FridaCLI().run()