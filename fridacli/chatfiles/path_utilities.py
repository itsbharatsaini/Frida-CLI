import os


def get_home_path():
    """"""
    return os.path.expanduser("~")


def get_current_dir() -> str:
    """"""
    return os.getcwd()


def get_sorted_file_list(path: str) -> list[str]:
    return sorted(os.listdir(path))


def format_path(path: str) -> str:
    """"""
    return path.replace("\\", "/")


def get_relative_path(path: str, dir: str = os.getcwd()) -> str:
    """Formats the given path and returns formatted as a relative path."""
    relative_path = os.path.relpath(path, f"{dir}/..")
    return format_path(relative_path)


def check_samepath(path1: str, path2: str) -> bool:
    """"""
    return os.path.realpath(path1) == os.path.realpath(path2)


def check_valid_dir(path: str) -> bool:
    """"""
    return os.path.exists(path) and os.path.isdir(path)


def change_directory(path: str) -> None:
    """"""
    os.chdir(path)
