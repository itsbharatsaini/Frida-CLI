from textual.screen import Screen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator
from textual.containers import Vertical, Horizontal
from fridacli.commands.recipes import generate_epics
from fridacli.logger import Logger
from fridacli.config import HOME_PATH
from typing import Iterable
from pathlib import Path

logger = Logger()
class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]

class DocGenerator(Screen):
    def compose(self):
        yield Vertical(
            Label("Working on your documentation!", id = "doc_title"),
            LoadingIndicator(),
            classes="loader",
        )
    

class EpicGenerator(Screen):
    path = HOME_PATH
    def compose(self):
        yield Vertical(
            Label("Please choose the destination folder where you'd like to save the file.", id="file_selection"),
            FilteredDirectoryTree(HOME_PATH, id="epic_generator_dir_selector"),
            Label("Write all the epics separated by commas", id="question"),
            Input(id="epics_text"),
            Horizontal( Button("Quit", variant="error", id="quit"), Button("Generate epics", variant="success", id="generate")),
            classes="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.pop_screen()
        elif event.button.id == "generate":
            epics_text = self.query_one("#epics_text", Input).value
            logger.info(__name__, epics_text)
            generate_epics(epics_text, self.path)
            self.app.pop_screen()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        self.path = event.path
        logger.info(__name__, self.path)
