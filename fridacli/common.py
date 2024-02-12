from fridacli.chatfiles.file_manager import FileManager
from fridacli.interface.bot_console import BotConsole
from fridacli.interface.system_console import SystemConsole
from fridacli.fridaCoder.frida_coder import FridaCoder
from chatbot.chatbot import ChatbotAgent

system_console = SystemConsole()
chatbot_console = BotConsole()
file_manager = FileManager()
frida_coder = FridaCoder(file_manager)
chatbot_agent = ChatbotAgent(file_manager)