import os
from dotenv import load_dotenv
from interface.styles import add_styletags_to_string

# API env variables
load_dotenv()
LLMOPS_FRIDACLI_API_KEY = os.getenv("LLMOPS_FRIDACLI_API_KEY")

# Chatbot env variables
BOT_NAME = "Frida"
INTERRUPT_CHAT = f"Press {add_styletags_to_string('Ctrl+C','operation')} (keyboard interrupt) to exit the chat"
WELCOME_SUBTITLE = add_styletags_to_string(
    "This is your personal "
    + add_styletags_to_string(f"{BOT_NAME} AI assistant", "bot")
    + ", you can ask any coding related question directly in the command line or type "
    + add_styletags_to_string("!help", "command")
    + " to see the available commands.",
    style="info",
)
