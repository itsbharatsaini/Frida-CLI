from typing import Dict
import os


config_file_path = f"{os.environ.get('HOME')}/.fridacli"
BOT_NAME = "Frida"


def config_file_exists() -> bool:
    """Check if the configuration file already exists."""
    return os.path.exists(config_file_path)


def get_config_vars(path: str) -> Dict:
    """Retrieve configuration variables from a given configuration file."""
    config_variables = {}
    with open(path, "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            config_variables[key] = value
    return config_variables
