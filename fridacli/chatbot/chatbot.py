import re
import logging
import textdistance as td

logging.basicConfig(level=logging.CRITICAL)

from softtek_llm.models import SofttekOpenAI
from softtek_llm.chatbots.chatbot import Chatbot

from chatbot.predefined_phrases import (
    chatbot_unauthorized,
    chatbot_badrequest,
    chatbot_error,
)
from config.env_vars import get_config_vars
from fridacli.interface.system_console import SystemConsole
from prompts.system import system_prompt

r"""
C:\Users\onder.campos\Documents\Innovation\asp_project
What is in the file Detalle_Hipotecario_DS.asp

C:\Users\onder.campos\Documents\Innovation\pythonProject
There is a error in main.py could you solve it with all the code
In the main.py file it is missing a funtion could you please use the funtion in utils.py so main.py could you it in one block code
what is in main.py give the code in it
Get me some code to check is a string is empty

Sure! Here's a code snippet in Python to check if a string is empty:

```python
def is_empty_string(string):
    if string == "":
        return True
    else:
        return False

# Example usage
my_string = "Hello, world!"
if is_empty_string(my_string):
    print("The string is empty.")
else:
    print("The string is not empty.")
```

This code defines a function `is_empty_string` that takes a string as a parameter. It checks if the string is empty by comparing it to an empty string `""`. If the string is empty, the function returns `True`, otherwise it returns `False`.

In the example usage, we create a variable `my_string` with the value `"Hello, world!"`. We then call the `is_empty_string` function with `my_string` as the argument and print the appropriate message based on the result.

Please let me know if you need the code in a different programming language.
Create the necessary code in the comment in rest.py

"""

system = SystemConsole()


class ChatbotAgent:
    SIMILARITY_THRESHOLD = 0.8

    def __init__(self, file_manager) -> None:
        env_vars = get_config_vars()

        self.__LLMOPS_API_KEY = env_vars["LLMOPS_API_KEY"]
        self.__CHAT_MODEL_NAME = env_vars["CHAT_MODEL_NAME"]
        self.__file_manager = file_manager
        self.__files_required = set()
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

        def generate_prompt(message):
            return f"""Create a list of steps and generate the necessary code, if needed, to solve the following instruction. 
If no programming language was specified, assume Python.
Try to do it in only one block of code.
\n{message}\n
When returning fenced code blocks in Markdown, enable syntax highlighting by specifying the programming language name in 
the same line right after the first three backticks.
In the first line, add a comment with a brief description (4 words) of the code.
"""

        def generate_prompt_with_files(message, files_required):
            # Generate a prompt by incorporating the required files.
            """
            Create a list of steps and generate the necessary code, if needed, to accomplish the following instruction.
            If files are mentioned, provide the necessary code without explicitly opening the file.
            Endeavor to complete this task using only one block of code.
            """
            lines = [
                message,
                "The files mentioned are:",
                """
Very important consideration:
When returning fenced code blocks in Markdown, enable syntax highlighting by specifying the programming language name. 
If the code within is intended for updating files, include the file name in a comment form like #filename.
""",
            ]

            for file in files_required:
                lines.append(f"{file}:")
                lines.append(self.__file_manager.get_file_content(file))

            result_string = "\n".join(lines)
            return result_string + "\n"

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
            if word in ["files", "file"]:
                key_words = True
        # If files are not in the context but the is key words, they might be referring to files without specified formats.
        if not self.is_files_open() and key_words:
            # TODO (IMPROVE) TWO SEARCHES NOT OPTIMAL
            # Get the files opened in dict format.
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

        if key_words and len(self.__files_required) == 0:
            # When keywords were mentioned but no files are present in the context, it indicates that no files were found.
            system.notification("NO FILES FOUND", bottom=0)
            return message

        if len(self.__files_required) > 0:
            # When files are in context, generate a prompt by incorporating the required files.
            message = generate_prompt_with_files(message, self.__files_required)
            return message
        return generate_prompt(message)

    def chat(self, message, special_prompt=False):
        try:
            if not special_prompt:
                message = self.decorate_prompt(message)
            response = self.__chatbot.chat(message)
            message = response.message.content
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
                print(e)
                error_message = chatbot_error

            system.notification(error_message, bottom=0)
            return "An error has occurred, see the message above."
        return message
