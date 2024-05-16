from textual.screen import Screen, ModalScreen
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
        return [path for path in paths if not path.name.startswith((".", "~"))]
    
class PathSelector(ModalScreen):
    def compose(self):
        yield Vertical(
            Label("Select the path to save your documentation:", classes="format_selection", shrink=True),
            FilteredDirectoryTree(HOME_PATH, id="configuration_documentation_path"),
            Label("Path selected:", classes="format_selection", shrink=True),
            Input(id="input_documentation_path", disabled=True),
            Horizontal(Button("Quit", variant="error"), Button("Confirm Path", variant="success", id="confirm_path_doc"), id="select_path_doc_horizontal"),
            id="path_selector_modal"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm_path_doc":
            path = self.query_one("#input_documentation_path", Input).value
            if path != "":
                self.dismiss(path)
            else:
                self.notify(f"You must select a valid path.")
        else:
            path = self.query_one("#input_documentation_path", Input).value
            self.dismiss(path)

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        tree_id = event.control.id
        if tree_id == "configuration_documentation_path":
            self.query_one("#input_documentation_path", Input).value = str(event.path)

class DocGenerator(Screen):
    def compose(self):
        yield Vertical(
            Label("Select the format(s) you need for your documentation:", classes="format_selection", shrink=True),
            Vertical(Checkbox("Word Document", id = "docx_check"), Checkbox("Markdown Readme", id = "md_check"), classes="vertical_documentation"),
            Label("Select the path to save your documentation:", classes="format_selection"),
            Horizontal(Button("Select path", id="select_path_button"), Input(id="input_doc_path",  disabled=True), classes="doc_generator_horizontal"),
            Label("Select if you want your code formatted after the documentation (only for C# and Python code):", classes="format_selection", shrink=True),
            Checkbox("Yes, use the formatter", id="use_formater"),
            Label("Select a method to generate the documentation:", classes="format_selection", shrink=True),
            Select(((line, line) for line in LINES), id="select_method", value="Quick (ChatGPT-3.5)"),
            Horizontal(Button("Quit", variant="error", id="quit"), Button("Create Documentation", variant="success", id="generate_documentation"), classes="doc_generator_horizontal"),
            classes="dialog_doc",
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if WorkerState.SUCCESS == event.worker.state and event.worker.name == "document_files":
            self.app.pop_screen(PathSelector)
            self.dismiss("OK")
        logger.info(__name__, f"{event}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.pop_screen()
        elif event.button.id == "select_path_button":
            self.app.push_screen(PathSelector(), self.select_doc_path_callback)
        elif event.button.id == "generate_documentation":
            docx = self.query_one("#docx_check", Checkbox).value
            md = self.query_one("#md_check", Checkbox).value
            path = self.query_one("#input_doc_path", Input).value
            method = self.query_one("#select_method", Select)
            if (docx or md) and path != "" and not method.is_blank():
                use_formatter = self.query_one("#use_formater", Checkbox).value
                self.app.push_screen(DocLoader())
                self.run_worker(document_files({"docx": docx, "md": md}, method.value.split(" ")[0]), exclusive=False, thread=True)
            else:
                self.notify(f"You must select at least one format and a method for the documentation.")

    def select_doc_path_callback(self, path):
        self.query_one("#input_doc_path", Input).value = path
            

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
