from textual.screen import Screen, ModalScreen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, Checkbox, Select, RadioSet, RadioButton, TextArea
from textual.containers import Vertical, Horizontal
from fridacli.commands.recipes import generate_epics, document_files
from textual.worker import Worker, WorkerState
from fridacli.file_manager import FileManager
from fridacli.logger import Logger
from fridacli.config import HOME_PATH, get_config_vars
from typing import Iterable
from pathlib import Path
import csv

logger = Logger()
file_manager = FileManager()
env_vars = get_config_vars()

LINES = """Quick (ChatGPT-3.5)
Slow (ChatGPT-4)
""".splitlines()

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith((".", "~"))]
    
class PathSelector(ModalScreen):
    def compose(self):
        logger.info(__name__, "Composing PathSelector")
        yield Vertical(
            Label("Select the path to save your documentation:", classes="format_selection", shrink=True),
            FilteredDirectoryTree(HOME_PATH, id="configuration_documentation_path"),
            Label("Path selected:", classes="format_selection", shrink=True),
            Input(id="input_documentation_path", disabled=True),
            Horizontal(Button("Quit", variant="error"), Button("Confirm Path", variant="success", id="confirm_path_doc"), id="select_path_doc_horizontal"),
            id="path_selector_modal"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
            Called when a button is pressed.
        """
        logger.info(__name__, f"(on_button_pressed) Button pressed: {event.button.id}")
        if event.button.id == "confirm_path_doc":
            path = self.query_one("#input_documentation_path", Input).value
            if path != "":
                self.dismiss(path)
            else:
                self.notify(f"You must select a valid path.")
        else:
            self.dismiss("")

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        """
            Called when a directory is selected.
        """
        logger.info(__name__, f"(on_directory_tree_directory_selected) Directory selected: {str(event.path)}")
        tree_id = event.control.id
        if tree_id == "configuration_documentation_path":
            self.query_one("#input_documentation_path", Input).value = str(event.path)

class DocGenerator(Screen):
    def compose(self):
        yield Vertical(
            Label("Select the format(s) you need for your documentation:", classes="format_selection", shrink=True),
            Vertical(Checkbox("Word Document", id = "docx_check"), Checkbox("Markdown Readme", id = "md_check"), classes="vertical_documentation"),
            Label("Select the path to save your documentation (the current directory is taken by default):", classes="format_selection"),
            Horizontal(Button("Select path", id="select_path_button"), Input(id="input_doc_path",  disabled=True, value=file_manager.get_folder_path()), classes="doc_generator_horizontal"),
            Label("Select if you want your code formatted after the documentation (only for C# and Python code):", classes="format_selection", shrink=True),
            Checkbox("Yes, use the formatter", id="use_formater"),
            Label("Select a method to generate the documentation:", classes="format_selection", shrink=True),
            Select(((line, line) for line in LINES), id="select_method", value="Quick (ChatGPT-3.5)"),
            Horizontal(Button("Quit", variant="error", id="quit"), Button("Create Documentation", variant="success", id="generate_documentation"), classes="doc_generator_horizontal"),
            classes="dialog_doc",
        )

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """
            Called when the worker state changes.
        """
        logger.info(__name__, f"(on_worker_state_changed) Worker state changed with event: {str(event)}")
        if WorkerState.SUCCESS == event.worker.state and event.worker.name == "document_files":
            self.app.pop_screen()
            self.dismiss("OK")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
            Called when a button is pressed.
        """
        logger.info(__name__, f"(on_button_pressed) Button pressed: {event.button.id}")
        if event.button.id == "quit":
            self.app.pop_screen()
        elif event.button.id == "select_path_button":
            self.app.push_screen(PathSelector(), self.select_doc_path_callback)
        elif event.button.id == "generate_documentation":
            docx = self.query_one("#docx_check", Checkbox).value
            md = self.query_one("#md_check", Checkbox).value
            doc_path = self.query_one("#input_doc_path", Input).value
            method = self.query_one("#select_method", Select)
            logger.info(__name__, f"(on_button_pressed) docx: {str(docx)} md: {str(md)} doc_path: {str(doc_path)} method: {str(method.value)}")
            if (docx or md) and doc_path != "" and not method.is_blank():
                use_formatter = self.query_one("#use_formater", Checkbox).value
                self.app.push_screen(DocLoader())
                self.run_worker(document_files({"docx": docx, "md": md}, method.value.split(" ")[0], doc_path, use_formatter), exclusive=False, thread=True)
            else:
                self.notify(f"You must select at least one format and a method for the documentation.")

    def select_doc_path_callback(self, path):
        """
            Callback for the path selection modal.
        """
        logger.info(__name__, f"(select_doc_path_callback) Path selected: {str(path)}")
        if path != "":
            self.query_one("#input_doc_path", Input).value = path
            

class DocLoader(Screen):
    def compose(self):
        logger.info(__name__, "Composing DocLoader")
        yield Vertical(
            Label("Working on your documentation!", id = "doc_title"),
            LoadingIndicator(),
            classes="loader",
        )

class EpicGenerator(Screen):
    path = HOME_PATH
    def compose(self):
        logger.info(__name__, "Composing EpicGenerator")
        yield Vertical(
            Label("Please choose the destination folder where you'd like to save the file.", id="file_selection"),
            FilteredDirectoryTree(HOME_PATH, id="epic_generator_dir_selector"),
            Label("Write all the epics separated by commas", id="question"),
            Input(id="epics_text"),
            Horizontal( Button("Quit", variant="error", id="quit"), Button("Generate epics", variant="success", id="generate")),
            classes="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
            Called when a button is pressed.
        """
        logger.info(__name__, f"(on_button_pressed) Button pressed: {event.button.id}")
        if event.button.id == "quit":
            self.app.pop_screen()
        elif event.button.id == "generate":
            epics_text = self.query_one("#epics_text", Input).value
            logger.info(__name__, f"(on_button_pressed) epics_text: {str(epics_text)}")
            generate_epics(epics_text, self.path)
            self.app.pop_screen()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        self.path = event.path
        logger.info(__name__, self.path)

class CreateNewEpic(Screen):
    path = HOME_PATH
    radio_set_value = ""
    csv_data = {}
    def compose(self):
        logger.info(__name__, "Composing CreateNewEpic")
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
        """
            Called when the radio set changes.
        """
        logger.info(__name__, f"(on_radio_set_changed) Radio set changed to: {event.pressed.label}")  
        self.radio_set_value = event.pressed.label


    def get_data_from_csv(self, path):
        """
            Get the data from the csv file
        """
        logger.info(__name__, f"get_data_from_csv Getting data from csv from path: {path}")
        try:
            epics = {}
            with open(path, "r") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    epic_name = row["epic"]
                    del row["epic"]
                    if epic_name != "":
                        if epics.get(epic_name, -1) == -1:
                            epics[epic_name] = [row]
                        else:
                            epics[epic_name].append(row)
            logger.info(__name__, f"(get_data_from_csv) Epics: {str(epics)}")
            return epics
        except Exception as e:
            logger.error(__name__, f"(get_data_from_csv) Error getting data from csv: {str(e)}")
            return {}

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
            Called when a button is pressed.
        """
        button_pressed = event.button.id
        logger.info(__name__, f"(on_button_pressed) Button pressed: {button_pressed}")
        if button_pressed == "create_epic_quit":
            self.app.pop_screen()
        elif button_pressed == "create_epic_generate":
            epic_name_input = self.query_one("#epic_name_input", Input).value
            plataform = str(self.radio_set_value)
            project_context_input = self.query_one("#project_context_input", TextArea).text
            logger.info(__name__, f"(on_button_pressed) epic_name_input: {str(epic_name_input)} plataform: {str(plataform)} project_context_input: {str(project_context_input)}")
            if len(epic_name_input) > 0  and len(plataform) > 0 and len(project_context_input) > 0:
                params = {"epic_name": epic_name_input, "plataform": plataform, "project_description": project_context_input}
                if self.csv_data != {}:
                    params["csv_data"] = self.csv_data
                #params = (epic_name_input, plataform, project_context_input)
                self.dismiss(params)
            else:
                self.notify("Some of the values are empty", severity="error")
        elif button_pressed == "upload_excel_button":
            """
                TODO: Implement the upload of the excel file
            """
            path = "Online Bookstore.csv"
            csv_data = self.get_data_from_csv(path)
            if csv_data != {}:
                self.csv_data = self.get_data_from_csv(path)
                self.notify("CSV data retrived successfully")
            else:
                self.notify("An error occurred while trying to get the data from the CSV file", severity="error")
            logger.info(__name__, "data from csv" + str(self.csv_data))


class ConfirmPushView(Screen):
    def __init__(self, text) -> None:
        super().__init__()
        self.text = text
    def compose(self):
        with Vertical(classes = "dialog_small"):
            yield Label(str(self.text), id="platform_label")
            with Horizontal(id="confirm_btns"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Confirm", variant="success", id="confirm")

    def on_button_pressed(self, event: Button.Pressed):
        """
            Called when a button is pressed.
        """
        button_pressed =  event.button.id
        logger.info(__name__, f"(on_button_pressed) Button pressed: {button_pressed}")
        if button_pressed == "cancel":
            self.app.pop_screen()
        elif button_pressed == "confirm":
            self.dismiss("")
