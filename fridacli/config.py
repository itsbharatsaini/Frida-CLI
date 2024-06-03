from typing import Dict
import os
import sys
from fridacli.logger import Logger

logger = Logger()

HOME_PATH = os.path.expanduser("~")
OS = "win" if sys.platform.startswith('win') else "linux"
config_file_path = f"{HOME_PATH}/.fridacli"
BOT_NAME = "Frida"
SUPPORTED_PROGRAMMING_LANGUAGES = [
    ".py",
    ".asp",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".js",
    ".html",
    ".css",
    ".php",
    ".rb",
    ".swift",
    ".go",
    ".lua",
    ".pl",
    ".r",
    ".sh",
]

if OS == "linux":
    import pwd

def config_file_exists(path: str = config_file_path) -> bool:
    """Check if the configuration file already exists."""
    logger.info(__name__, f"(config_file_exists) Checking if the configuration file exists in path: {path}")
    return os.path.exists(path)


def get_config_vars(path: str = config_file_path) -> Dict:
    """Retrieve configuration variables from a given configuration file."""
    logger.info(__name__, f"(get_config_vars) Getting configuration variables from path: {path}")
    if not config_file_exists():
        keys = {}
        
        keys["PROJECT_PATH"] = ""
        keys["LOGS_PATH"] = ""
        keys["LLMOPS_API_KEY"] = ""
        keys["CHAT_MODEL_NAME"] = ""
        keys["CHAT_MODEL_NAME_V4"] = ""
        keys["PYTHON_ENV_PATH"] = ""
        write_config_to_file(keys)
        
    config_variables = {}
    with open(path, "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            config_variables[key] = value
    logger.info(__name__, f"(get_config_vars) Configuration variables: {config_variables}")
    return config_variables


def get_username() -> str:
    """Returns the name of the current user."""
    logger.info(__name__, "(get_username) Getting the username")
    try:
        if OS == "win":
            return os.getlogin()
        else:
            uid = os.geteuid()
            user_info = pwd.getpwuid(uid)
            return user_info.pw_name
    except OSError:
        username = "user"
    return username


def write_config_to_file(keys: dict, path: str = config_file_path) -> None:
    """Write the configuration file with the API key."""
    logger.info(__name__, f"(write_config_to_file) Writing configuration file with keys: {str(keys)} in path: {str(path)}")
    try:
        if config_file_exists():
            os.remove(path)
        for key, value in keys.items():
            command = f"echo {key}={value} >> {path}"
            os.system(command)
    except Exception as e:
        logger.error(__name__, f"Error configurating api keys: {str(e)}")


def read_config_file(path: str = config_file_path) -> str:
    """Read the contents of a configuration file and returns it."""
    logger.info(__name__, f"(read_config_file) Reading configuration file in path: {path}")
    try:
        with open(path, "r") as file_content:
            configfile_content = file_content.read()
        return configfile_content.rstrip("\n")
    except Exception as e:
        logger.error(__name__, f"Error reading cong file: {str(e)}")


def get_vars_as_dict():
    """Get the variables as a dictionary."""
    logger.info(__name__, "(get_vars_as_dict) Getting the variables as a dictionary")
    result_dict = {
        key_value.split("=")[0]: key_value.split("=")[1]
        for key_value in read_config_file().split("\n")
    }
    return result_dict
