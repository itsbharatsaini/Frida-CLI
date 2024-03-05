import os
import logging
import datetime

class Logger:
    _instance = None
    _log_file_name = "app.log"
    _stat_file_name = "stats.log"
    def __new__(cls, file_location="./"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.LOG_FILE_LOCATION = f"{file_location}{cls._log_file_name}"
            cls._instance.STATS_FILE_LOCATION = f"{file_location}{cls._stat_file_name}"
            cls._instance.setup_logger()
        return cls._instance

    def setup_logger(self):
        os.makedirs(os.path.dirname(self.LOG_FILE_LOCATION), exist_ok=True)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(self.LOG_FILE_LOCATION)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(file_handler)

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

    def update_log_paths(self, file_location):
        self.LOG_FILE_LOCATION = f"{file_location}{self._log_file_name}"
        self.STATS_FILE_LOCATION = f"{file_location}{self._stat_file_name}"
        self.setup_logger()

