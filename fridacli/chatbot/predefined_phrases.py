from fridacli.config.env_vars import BOT_NAME
from fridacli.interface.styles import add_styletags_to_string

# Chat session's bot messages
START_MESSAGE = "Hello! How may I help you?"
INTERRUPT_CHAT = f"Press {add_styletags_to_string('Ctrl+C','operation')} (keyboard interrupt) to exit the chat"
WELCOME_PANEL_MESSAGE = add_styletags_to_string(
    "Welcome to your personal "
    + add_styletags_to_string(f"{BOT_NAME} AI assistant", "bot")
    + ", you can ask any coding related question directly in the command line or type "
    + add_styletags_to_string("!help", "command")
    + " to see the available commands.",
    style="info",
)
CONFIGFILE_OVERWRITE = (
    "A configuration file already exists. Do you want to overwrite it?"
)

message_config_file_path = (
    lambda path: f"Configuration file path: {add_styletags_to_string(path,style='path')}"
)

# Error messages
ERROR_STR = "This is not a coding related question, is there anything else I can assist you with?"
ERROR_MISSING_CONFIGFILE = f"Missing configuration file. Execute {add_styletags_to_string('frida config', style='code')} to create it."
ERROR_INVALID_COMMAND = lambda subcommand: (
    f"{add_styletags_to_string('Error:', style='error')} {add_styletags_to_string(subcommand, style='code')} command not found."
)

# Success messages
success_configfile_create = (
    lambda path: f"Configuration file {add_styletags_to_string(path, style='path')} "
    + f"{add_styletags_to_string(f'successfully created', style='success')}."
)
success_configfile_update = (
    lambda path: f"Configuration file {add_styletags_to_string(path, style='path')} "
    + f"{add_styletags_to_string(f'successfully updated', style='success')}."
)

chatbot_unauthorized = f"{add_styletags_to_string('Unauthorized', style='error')}: The provided API key is invalid or missing\nExecute {add_styletags_to_string('frida config', style='code')} to update it."
chatbot_badrequest = f"{add_styletags_to_string('Bad Request', style='error')}: Chatbot model not found, please update model name\nExecute {add_styletags_to_string('frida config', style='code')} to update it."
chatbot_error = f"{add_styletags_to_string('Bad Request', style='error')}: One or all of the configuration keys is invalid or missing\nExecute {add_styletags_to_string('frida config', style='code')} to update it."
chatbot_with_file_prompt = """
Very important consideration:
When returning fenced code blocks in Markdown, enable syntax highlighting by specifying the programming language name. 
If the code within is intended for updating files, include the file name in a comment form like #filename.
The files mentioned are:
"""

chatbot_without_file_prompt = lambda message: f"""Create a list of steps and generate the necessary code, if needed, to solve the following instruction. 
If no programming language was specified, assume Python.
Try to do it in only one block of code.
\n{message}\n
When returning fenced code blocks in Markdown, enable syntax highlighting by specifying the programming language name in 
the same line right after the first three backticks.
In the first line, add a comment with a brief description (4 words) of the code.
"""
