from .document_recipe import exec_document
from .epics_generator import exec_generate_epics
from fridacli.chatbot import ChatbotAgent
from fridacli.file_manager import FileManager
from fridacli.frida_coder import FridaCoder


chatbot_agent = ChatbotAgent()
file_manager = FileManager()
frida_coder = FridaCoder()

async def document_files(checkbox):
    return await exec_document(checkbox, chatbot_agent, file_manager, frida_coder)

def generate_epics(text, path):
    exec_generate_epics(chatbot_agent, text, path)
