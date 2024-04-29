from textual.screen import Screen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, Checkbox, Select
from textual.containers import Vertical, Horizontal
from fridacli.commands.recipes import generate_epics, document_files
from textual.worker import Worker, WorkerState
from fridacli.logger import Logger
from fridacli.config import HOME_PATH
from typing import Iterable
from pathlib import Path

logger = Logger()

LINES = """Quick (ChatGPT-3.5)
Slow (ChatGPT-4)
""".splitlines()

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]

class DocGenerator(Screen):
    def compose(self):
        yield Vertical(
            Label("Please select the format(s) you need for your documentation:", id="format_selection"),
            Vertical(Checkbox("Word Document", id = "docx_check"), Checkbox("Markdown Readme", id = "md_check"), id="checkbox"),
            Label("Please select a method to generate the documentation:"),
            Select(((line, line) for line in LINES), id="select_method", value="Quick (ChatGPT-3.5)"),
            Horizontal(Button("Quit", variant="error", id="quit"),Button("Create Documentation", variant="success", id="generate_documentation")),
            classes="dialog_doc",
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if WorkerState.SUCCESS == event.worker.state and event.worker.name == "document_files":
            self.app.pop_screen()
            self.dismiss("OK")
        logger.info(__name__, f"{event}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.pop_screen()
        elif event.button.id == "generate_documentation":
            docx = self.query_one("#docx_check", Checkbox).value
            md = self.query_one("#md_check", Checkbox).value
            method = self.query_one("#select_method", Select)
            if (docx or md) and not method.is_blank():
                self.app.push_screen(DocLoader())
                self.run_worker(document_files({"docx": docx, "md": md}, method.value.split(" ")[0]), exclusive=False, thread=True)
            else:
                self.notify(f"You must select at least one format and a method for the documentation.")
            

class DocLoader(Screen):
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
