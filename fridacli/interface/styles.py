from pandas import DataFrame
from rich import box
from rich.columns import Columns
from rich.table import Table

import os
import re
from typing import Iterable


def add_styletags_to_string(string: str, style: str) -> str:
    """Returns a modified string with style tags added."""
    return f"[{style}]{string}[/]"


def add_styletags_from_regex(string: str) -> str:
    """Returns a modified string with style tags
    added based on predefined regex patterns."""
    regex_patterns = [
        (r"!([\w-]+)", r"[command]!\1[/]"),
        (r"-([\w-]+)", r"[option]-\1[/]"),
        (r"<([^<>]+)>", r"[operation]<\1>[/]"),
    ]

    # Iterate over the patterns and apply the corresponding formatting
    for pattern, replacement in regex_patterns:
        string = re.sub(pattern, replacement, string)

    return string


def print_padding(padding: int = 1) -> None:
    """Print new lines based on the value of the padding parameter."""
    if padding > 0:
        print("\n" * (padding - 1))


def format_path(path: str, dir: str = os.getcwd()) -> str:
    """Formats the given path and returns formatted as a relative path."""
    relative_path = os.path.relpath(path, f"{dir}/..")
    return relative_path.replace("\\", "/")


def format_to_columns(iterables: Iterable):
    """"""
    columns_output = Columns(iterables, equal=True, expand=True)
    return columns_output


def format_to_table(
    data: DataFrame,
    title: str = None,
    show_header: bool = True,
    box=box.ROUNDED,
    expand: bool = False,
    padding: bool = False,
    border_color: str = "",
    text_color: str = None,
    ratio: list = [],
) -> Table:
    """"""
    table = Table(
        title=title,
        show_header=show_header,
        box=box,
        expand=expand,
        padding=(0, 3, 1 if padding else 0, 1),
        style=border_color,
    )

    for iterator, column in enumerate(data.columns.to_list()):
        column_ratio = ratio[iterator] if ratio else 0
        table.add_column(column, ratio=column_ratio)

    for i, row in data.iterrows():
        row_data = list(map(str, row.tolist()))
        if text_color:
            row_data = [
                add_styletags_to_string(element, text_color) for element in row_data
            ]
        table.add_row(*row_data)

    return table


def file_list_with_styles(file_list: list) -> list:
    """"""
    return [
        add_styletags_to_string(f"{element}/", "path")
        if os.path.isdir(element)
        else add_styletags_to_string(element, "info")
        for element in file_list
    ]
