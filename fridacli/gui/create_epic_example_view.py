from textual.containers import  VerticalScroll, Vertical, Horizontal
from textual.screen import Screen
from textual.events import Focus, Hide, Show
from textual.widgets import DirectoryTree, Static, Select, Button
from fridacli.commands.recipes import document_files
from fridacli.config import get_vars_as_dict
from rich.traceback import Traceback
from fridacli.logger import Logger
from textual.reactive import var
from rich.syntax import Syntax
from typing import Iterable
from pathlib import Path
from .push_screens import CreateNewEpic
import os

logger = Logger()

class Create_epic_example(Static):
    CSS_PATH = "tcss/frida_styles.tcss"
    recipe_selected = ""

    def compose(self):
        with Horizontal():
            yield Button("Execute", id="show_create_epic_view")
    
    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        logger.info(__name__, button_pressed)
        if button_pressed == "show_create_epic_view" :
            self.app.push_screen(CreateNewEpic())
