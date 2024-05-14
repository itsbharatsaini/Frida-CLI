from textual.screen import Screen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, Checkbox, RadioSet, RadioButton, TextArea
from textual.containers import Vertical, Horizontal
from fridacli.commands.recipes import generate_epics, document_files
from textual.worker import Worker, WorkerState
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
            Label("Please select the format(s) you need for your documentation.", id="format_selection"),
            Vertical(Checkbox("Word Document", id = "docx_check"), Checkbox("Markdown Readme", id = "md_check"), id="checkbox"),
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
            if docx or md:
                self.app.push_screen(DocLoader())
                self.run_worker(document_files({"docx": docx, "md": md}), exclusive=False, thread=True)
            else:
                self.notify(f"You must select at least one option.")

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

class CreateNewEpic(Screen):
    path = HOME_PATH
    radio_set_value = ""
    def compose(self):
        yield Vertical(
            Input(placeholder="Name of project", id="epic_name_input"),
            Label("Type of Platform", id="platform_label"),
            RadioSet(RadioButton("Mobile"), RadioButton("Web"), RadioButton("Tablet"), id="platform_radio"),
            Label("Tell us more about your project", id="project_context_label"),
            TextArea("", id="project_context_input"),
            Label("Upload your Excel", id="upload_excel_label"),
            Horizontal(
                Button("Upload your Excel", variant="default", id="upload_excel_button"),
                Button("Download Template", variant="default", id="download_template_button")
            ),
            Horizontal(
                Button("Cancel", variant="error", id="create_epic_quit"),
                Button("Create epic", variant="success", id="create_epic_generate")
            ),
            classes="dialog",
        )
    def on_radio_set_changed(self, event: RadioSet.Changed):
        self.radio_set_value = event.pressed.label
        logger.info(__name__, self.radio_set_value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_epic_quit":
            self.app.pop_screen()
        elif event.button.id == "create_epic_generate":
            epic_name_input = self.query_one("#epic_name_input", Input).value
            plataform = str(self.radio_set_value)
            project_context_input = self.query_one("#project_context_input", TextArea).text
            if len(epic_name_input) > 0  and len(plataform) > 0 and len(project_context_input) > 0:
                params = (epic_name_input, plataform, project_context_input)
                self.dismiss(params)
            else:
                self.notify("Some of the values are empty", severity="error")
