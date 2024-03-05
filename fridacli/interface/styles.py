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
