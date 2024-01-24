from fridacli.interface.styles import add_styletags_to_string


CONFIGFILE_OVERWRITE = (
    "A configuration file already exists. Do you want to overwrite it?"
)
message_config_file_path = (
    lambda path: f"Configuration file path: {add_styletags_to_string(path,style='path')}"
)
ERROR_MISSING_CONFIGFILE = f"Missing configuration file. Execute {add_styletags_to_string('frida config', style='code')} to create it."
success_configfile_create = (
    lambda path: f"Configuration file {add_styletags_to_string(path, style='path')} "
    + f"{add_styletags_to_string(f'successfully created', style='success')}."
)
success_configfile_update = (
    lambda path: f"Configuration file {add_styletags_to_string(path, style='path')} "
    + f"{add_styletags_to_string(f'successfully updated', style='success')}."
)
