from fridacli.interface.styles import add_styletags_to_string

START_MESSAGE = "Hello! How may I help you?"

# Error messages
ERROR_STR = "This is not a coding related question, is there anything else I can assist you with?"
ERROR_MISSING_CONFIGFILE = f"Missing configuration file. Execute {add_styletags_to_string('frida config', style='command')} to create it."

# Success messages
success_configfile_create = (
    lambda path: f"Configuration file {add_styletags_to_string(path, style='path')} "
    + f"{add_styletags_to_string(f'successfully created', style='success')}."
)
success_configfile_update = (
    lambda path: f"Configuration file {add_styletags_to_string(path, style='path')} "
    + f"{add_styletags_to_string(f'successfully updated', style='success')}."
)
