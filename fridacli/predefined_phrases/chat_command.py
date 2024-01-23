from fridacli.interface.styles import add_styletags_to_string


ERROR_PATH_DOES_NOT_EXIST = (
    lambda path: f"{add_styletags_to_string('Error:', 'error')} "
    + f"{add_styletags_to_string(path, 'path')} "
    + "directory does not exist"
)
WARNING_ARGUMENT_REQUIRED = (
    lambda argument: f"{add_styletags_to_string(argument,'option')} argument is required. "
    + f"Type {add_styletags_to_string('!help', 'code')} for more info"
)
CONFIRM_RELOAD_PROJECT = "Reload open project?"
CONFIRM_OPEN_NEW_PROJECT = "Close current project and open new folder?"
PWD_COMMAND_OUTPUT = (
    lambda path: f"Current directory: {add_styletags_to_string(path, 'path')}"
)
