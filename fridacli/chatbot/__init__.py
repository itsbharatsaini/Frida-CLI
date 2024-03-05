import re
import logging
import textdistance as td

from softtek_llm.models import SofttekOpenAI
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
#from fridacli.logger import Logger


class ChatbotAgent:
    SIMILARITY_THRESHOLD = 0.8

    def __init__(self) -> None:
        env_vars = get_config_vars()
        print(env_vars)

        self.__LLMOPS_API_KEY = env_vars["LLMOPS_API_KEY"]
        self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME"]

        self.__files_required = set()
        self.__file_manager = FileManager()
        self.__build_model()

    def __build_model(self):
        model = SofttekOpenAI(
            api_key=self.__LLMOPS_API_KEY, model_name=self.__CHAT_MODEL_NAME
        )
        self.__chatbot = Chatbot(model=model, description=system_prompt)

    def is_files_open(self):
        return len(self.__files_required) > 0

    def get_files_required(self):
        return self.__files_required

    def decorate_prompt(self, message):
        def is_file_format(word):
            # Determine if a word follows the file format (name.extension).
            extensions = [".py", ".asp"]
            pattern = f'^[a-zA-Z_][a-zA-Z0-9_]*({ "|".join(extensions)})$'
            match = re.match(pattern, word)
            return bool(match)

        def generate_talk_prompt(message):
            return chatbot_talk_prompt(message)

        """
        talk_or_solve = self.__chatbot.chat(chatbot_classification_prompt(message))
        print("talk_or_solve", talk_or_solve.message.content)
        if talk_or_solve.message.content == "solve":
        """
        #logger.info(__name__, f"Decorating prompt")
        self.__files_required = set()
        key_words = False
        # Divide the user message into words.
        words = message.split(" ")
        for word in words:
            # Search for words with file format (name.extension).
            if is_file_format(word):
                # Add files to context
                self.__files_required.add(word)
            # Search for key words related with files usage.
            if word in ["files", "file", "archivo", "archivos"]:
                key_words = True
        # If files are not in the context but the is key words, they might be referring to files without specified formats.
        if key_words and len(self.__file_manager.get_files()) == 0:
            pass
            #system.notification("NO PROJECT OPEN")

        if not self.is_files_open() and key_words:
            try:
                """
                TODO (IMPROVE) TWO SEARCHES NOT OPTIMAL
                Get the files opened in dict format.
                """
                file_list = self.__file_manager.get_files()
                files_to_search = {
                    filename.rsplit(".", 1)[0]: filename for filename in file_list
                }
                for word in words:
                    # Check all words for similarity with the open name files that meet the specified SIMILARITY_THRESHOLD.
                    similarity_perc = [
                        {fr: similarity}
                        for fr, similarity in (
                            (fr, td.jaccard.normalized_similarity(word, fr))
                            for fr in list(files_to_search.keys())
                        )
                        if similarity >= self.SIMILARITY_THRESHOLD
                    ]
                    if len(similarity_perc) > 0:
                        # Get the highest similarity file name, and get file name with extension.
                        file_required = max(
                            similarity_perc, key=lambda x: list(x.values())[0]
                        )
                        file_required = list(file_required.keys())[0]
                        # Add files to context
                        self.__files_required.add(files_to_search.get(file_required))
            except Exception as e:
                pass
                #logger.error(__name__, f"Error seraching for similarity: {e}")

        if key_words and len(self.__files_required) == 0:
            # When keywords were mentioned but no files are present in the context, it indicates that no files were found.
            #system.notification("NO FILES FOUND", bottom=0)
            return message

        if len(self.__files_required) > 0:
            # When files are in context, generate a prompt by incorporating the required files.
            message = generate_prompt_with_files(
                message, self.__files_required, self.__file_manager
            )
            return message
        return chatbot_without_file_prompt(message)

    def __exec_chat(self, message: str):
        #logger.info(__name__, f"Exec chat")
        try:
            response = self.__chatbot.chat(message)
            """
            logger.stat_tokens(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
            )  
            """
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
                #logger.error(__name__, f"An error has occurred using chat funtion: {e}")
                error_message = chatbot_error

            #system.notification(error_message, bottom=0)
            return "An error has occurred, see the message above."

    def chat(self, message, special_prompt=False):
        """
        TODO:
            The chatbot is incapable to response simple questions like:
            how are you, since it tries to responde with code
        """

        response = ""
        if not special_prompt:
            message = self.decorate_prompt(message)
            response = self.__exec_chat(message)
            return response

        response = self.__exec_chat(message)
        return response
