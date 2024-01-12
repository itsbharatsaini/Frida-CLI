import logging
from chatbot.predefined_phrases import chatbot_unauthorized, chatbot_badrequest, chatbot_error

logging.basicConfig(level=logging.CRITICAL)

from softtek_llm.models import SofttekOpenAI
from softtek_llm.chatbots.chatbot import Chatbot
from prompts.system import system_prompt
from config.env_vars import get_config_vars

from fridacli.interface.system_console import SystemConsole

system = SystemConsole()

class ChatbotAgent:
    def __init__(self) -> None:
        env_vars = get_config_vars()

        self.__LLMOPS_API_KEY = env_vars["LLMOPS_API_KEY"]
        self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME"]
        self.__build_model()

    def __build_model(self):
        model = SofttekOpenAI(
            api_key=self.__LLMOPS_API_KEY, model_name=self.__CHAT_MODEL_NAME
        )
        self.__chatbot = Chatbot(model=model, description=system_prompt)

    def chat(self, message):
        try:
            response = self.__chatbot.chat(message)
            message = response.message.content
        except Exception as e:
            if e == "Unauthorized":
                system.notification(chatbot_unauthorized)
            elif (
                type(e) is str and "Bad Request: The API deployment for this resource does not exist." in e 
            ):
                system.notification(chatbot_badrequest)
            else:
                system.notification(chatbot_error)
            return "An error has occurred, see the message above."
        return message
