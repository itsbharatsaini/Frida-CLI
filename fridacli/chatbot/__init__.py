import re
import textdistance as td
from softtek_llm.models import SofttekOpenAI
from softtek_llm.memory import WindowMemory
from softtek_llm.chatbots.chatbot import Chatbot
from .predefined_phrases import (
    chatbot_unauthorized,
    chatbot_badrequest,
    chatbot_error,
    chatbot_with_file_prompt,
    chatbot_without_file_prompt,
    chatbot_classification_prompt,
    chatbot_talk_prompt,
    generate_prompt_with_files,
)
from fridacli.config import get_config_vars
from fridacli.prompts_provider.chatbot_prompts import system_prompt
from fridacli.file_manager import FileManager
from fridacli.logger import Logger
from fridacli.config import SUPPORTED_PROGRAMMING_LANGUAGES

logger = Logger()


class ChatbotAgent:
    _instance = None
    SIMILARITY_THRESHOLD = 0.8

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatbotAgent, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance        

    def __init__(self) -> None:
        env_vars = get_config_vars()

        self.__LLMOPS_API_KEY = env_vars["LLMOPS_API_KEY"]
        self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME"]

        self.__files_required = set()
        self.__file_manager = FileManager()
        logger.info(__name__, f"""ChatbotAgent init
            Model name: {self.__CHAT_MODEL_NAME}
            LLMOPS API key: {self.__LLMOPS_API_KEY}
        """)
        self.__build_model()
    
    def update_env_vars(self):
        env_vars = get_config_vars()

        self.__LLMOPS_API_KEY = env_vars["LLMOPS_API_KEY"]
        self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME"]
        self.__build_model()

    def __build_model(self):
        """
            Build the chatbot model using the SofttekOpenAI model.
        """
        logger.info(__name__, "Building model")
        model = SofttekOpenAI(
            api_key=self.__LLMOPS_API_KEY, model_name=self.__CHAT_MODEL_NAME
        )
        self.context = WindowMemory(window_size=10)
        self.__chatbot = Chatbot(model=model, description=system_prompt, memory=self.context)

    def is_files_open(self):
        """
            Determine if there are files in context.
        """
        logger.info(__name__, f"(is_files_open) Files required: {len(self.__files_required)}")
        return len(self.__files_required) > 0
    
    def change_version(self, version=4):
        logger.info(__name__, f"(change_version) Changing model version to: {version}")
        env_vars = get_config_vars()
        if version == 3:
            if self.__CHAT_MODEL_NAME != env_vars["CHAT_MODEL_NAME"]:
                self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME"]
                self.__build_model()
                logger.info(__name__, f"Model changed to: {self.__chatbot.model.model_name}")
        elif version == 4:
            if self.__CHAT_MODEL_NAME != env_vars["CHAT_MODEL_NAME_V4"]:
                self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME_V4"]
                self.__build_model()
                logger.info(__name__, f"Model changed to: {self.__chatbot.model.model_name}")

    def get_files_required(self):
        """
            Get the files required in context.
        """
        logger.info(__name__, f"(get_files_required) Files required: {str(self.__files_required)}")
        return self.__files_required

    def add_files_required(self, files, special_file):
        """
            Add files to the context.
        """
        logger.info(__name__, f"(add_files_required) Adding files to context with files: {str(files)} and special_file: {special_file}")
        if len(files) > 0:
            for file in files:
                self.__files_required.add(file)

        if special_file != "":
            self.__files_required.add(special_file)

    def is_file_format(self, word):
        """
            Determine if a word follows the file format (name.extension).
        """
        logger.info(__name__, f"(is_file_format) Checking if word: {word} is file format")
        pattern = f'^[a-zA-Z_][a-zA-Z0-9_]*({ "|".join(SUPPORTED_PROGRAMMING_LANGUAGES)})$'
        match = re.match(pattern, word)
        logger.info(__name__, f"(is_file_format) Word: {word} is file format: {str(bool(match))}")
        return bool(match)

    def get_matching_files(self, message, available_files):
        """
            Get the matching files in the message.
        """
        logger.info(__name__, f"(get_matching_files) Getting matching files in message: {str(message)}")
        message_words = message.split(" ")
        located_files = []

        all_files = self.__file_manager.get_files()

        for word in message_words:
            if self.is_file_format(word):
                if word in all_files and word not in available_files:
                    located_files.append(self.__file_manager.get_file_path(word))

        return located_files
    

    def decorate_prompt(self, message):
        """
            Decorate the prompt with the required files.
        """

        logger.info(__name__, f"(decorate_prompt) Decorating prompt: {message}")

        if len(self.__files_required) > 0:
            # When files are in context, generate a prompt by incorporating the required files.
            message = generate_prompt_with_files(
                message, self.__files_required, self.__file_manager
            )
            return message
        return chatbot_without_file_prompt(message)

    def __exec_chat(self, message: str):
        """
            Execute the chat function.
        """
        try:
            response = self.__chatbot.chat(message)
            logger.info(__name__, f"(__exec_chat) Prompt tokens: {response.usage.prompt_tokens}, Response tokens: {response.usage.completion_tokens}, Chat response: {response}")
            return response.message.content
        except Exception as e:
            if e == "Unauthorized":
                error_message = chatbot_unauthorized
            elif (
                type(e) is str
                and "Bad Request: The API deployment for this resource does not exist."
                in e
            ):
                error_message = chatbot_badrequest
            else:
                # logger.error(__name__, f"An error has occurred using chat funtion: {e}")
                error_message = chatbot_error

            # system.notification(error_message, bottom=0)
            return "An error has occurred"

    def clear_context(self):
        """
            Clear the context.
        """
        logger.info(__name__, "(clear_context) Clearing context")
        self.context.clear_messages()

    def chat(self, message, special_prompt=False):
        """
        TODO:
            The chatbot is incapable to response simple questions like:
            how are you, since it tries to responde with code
        """
        self.update_env_vars()
        logger.info(__name__, f"(chat) Chat with message: {message} and special_prompt: {special_prompt}")
        response = ""
        if not special_prompt:
            logger.info(__name__, "helloooo")
            message = self.decorate_prompt(message)
            logger.info(__name__, f"Decorated message: {message}")
            response = self.__exec_chat(message)
            return response

        response = self.__exec_chat(message)
        return response
