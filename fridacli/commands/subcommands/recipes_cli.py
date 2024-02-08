from fridacli.commands.recipes.angular_voyager import exec_angular_voyager
from fridacli.commands.recipes.asp_voyager import exec_asp_voyager
from fridacli.interface.system_console import SystemConsole
from fridacli.chatfiles.file_manager import FileManager
from fridacli.chatbot.chatbot import Chatbot
from fridacli.interface.bot_console import BotConsole
import os

def angular_voyager(args = None):
    """
    Recipe that migrates a angular project from an old version to a new version
    """
    path = args if args is not None else os.getcwd()
    exec_angular_voyager(path)

def asp_voyager(*args, **kwargs):
    """
    Recipe that migrates a asp project from an old version to a new version
    """
    system_console: SystemConsole = kwargs.get("system_console")
    file_manager: FileManager = kwargs.get("file_manager")
    chatbot_agent: Chatbot = kwargs.get("chatbot_agent")
    chatbot_console: BotConsole = kwargs.get("chatbot_console")
    
    exec_asp_voyager(file_manager, chatbot_agent, chatbot_console)

