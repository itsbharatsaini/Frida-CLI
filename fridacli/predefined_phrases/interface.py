from fridacli.config.env_vars import BOT_NAME
from fridacli.interface.styles import add_styletags_to_string


INTERRUPT_CHAT = f"Press {add_styletags_to_string('Ctrl+C','operation')} (keyboard interrupt) to exit the chat"
WELCOME_PANEL_MESSAGE = add_styletags_to_string(
    "Welcome to your personal "
    + add_styletags_to_string(f"{BOT_NAME} AI assistant", "bot")
    + ", you can ask any coding related question directly in the command line or type "
    + add_styletags_to_string("!help", "command")
    + " to see the available commands.",
    style="info",
)
