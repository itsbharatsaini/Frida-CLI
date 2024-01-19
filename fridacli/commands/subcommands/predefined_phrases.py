from fridacli.interface.styles import add_styletags_to_string


ERROR_PATH_DOES_NOT_EXIST = (
    lambda path: f"{add_styletags_to_string('Error:', 'error')} "
    + f"{add_styletags_to_string(path, 'path')} "
    + "directory does not exist"
)
