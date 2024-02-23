import os
import logging
import datetime
import time
import logging
from fridacli.config.env_vars import HOME_PATH


class Logger:
    LOG_FILE_LOCATION = f"{HOME_PATH}/Documents/fridalogs/app.log"
    STATS_FILE_LOCATION = f"{HOME_PATH}/Documents/fridalogs/stats.log"

    logger = None
    stat_loger = None

    def __init__(self):
        os.makedirs(f"{HOME_PATH}/Documents/fridalogs/", exist_ok=True)
        self.setup_logger()

    @classmethod
    def setup_logger(cls):
        cls.logger = logging.getLogger()
        cls.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(cls.LOG_FILE_LOCATION)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        cls.logger.handlers = []
        cls.logger.addHandler(file_handler)

    def info(self, position, text):
        self.logger.info("%s - %s - %s", position, "INFO", text)

    def error(self, position, text):
        self.logger.error("%s - %s - %s", position, "ERROR", text)

    def __write_log_stat(self, position: str, log_type: str, text: str):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.STATS_FILE_LOCATION, "a") as f:
            line = f"{formatted_time} - {position} - {log_type} - {text}\n"
            f.write(line)

    def stat_tokens(self, prompt_tokens, completion_tokens):
        self.__write_log_stat(
            "Tokens",
            "STAT",
            f"prompt_tokens: {prompt_tokens}, completion_tokens:{completion_tokens}",
        )


"""

class Logger:

    LOG_FILE_LOCATION = "app.log"
    STATS_FILE_LOCATION = "stats.log"

    def __write_log(self, position: str, log_type: str, text: str):
        try:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.LOG_FILE_LOCATION, "a") as f:
                line = f"{formatted_time} - {position} - {log_type} - {text}\n"
                f.write(line)
                f.flush()
        except Exception as e:
            print("Error:", e)

    def __write_log_stat(self, position: str, log_type: str, text: str):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.STATS_FILE_LOCATION, "a") as f:
            line = f"{formatted_time} - {position} - {log_type} - {text}\n"
            f.write(line)

    def info(self, position: str, text: str):
        self.__write_log(position, "INFO", text)

    def error(self, position: str, text: str):
        self.__write_log(position, "ERROR", text)

    def stat_tokens(self, prompt_tokens, completion_tokens):
        self.__write_log_stat(
            "Tokens",
            "STAT",
            f"prompt_tokens: {prompt_tokens}, completion_tokens:{completion_tokens}",
        )
"""
