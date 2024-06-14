from textual.events import Mount
from textual.screen import Screen, ModalScreen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, Checkbox, Select, RadioSet, RadioButton, TextArea, Markdown
from textual.containers import Vertical, Horizontal, VerticalScroll
from fridacli.commands.recipes import generate_epics, document_files, migrate_files
from fridacli.config import HOME_PATH, get_config_vars
from textual.containers import Vertical, Horizontal
from textual.screen import Screen, ModalScreen
from textual.worker import Worker, WorkerState
from fridacli.file_manager import FileManager
from fridacli.logger import Logger
from typing import Iterable
from pathlib import Path
import csv
import os


logger = Logger()
file_manager = FileManager()
env_vars = get_config_vars()

METHOD_LINES = ["Quick (ChatGPT-3.5)", "Slow (ChatGPT-4)"]
PROGRAMMING_LANGUAGE = ["Java"]
LANGUAGE_VERSIONS = {
    "Java": ["Java SE 8", "Java SE 9", "Java SE 10", "Java SE 11", "Java SE 12"]
}

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith((".", "~"))]
    
class PathSelector(ModalScreen):
    def __init__(self, only_directories = True, allow_special= False) -> None:
        self.only_directories = only_directories
        self.allow_special = allow_special
        super().__init__()

    def compose(self):
        logger.info(__name__, "Composing PathSelector")
        with Vertical(id="path_selector_modal"):
            yield Label("Select the path to save your documentation:", classes="format_selection", shrink=True)
            if self.allow_special:
                yield DirectoryTree(HOME_PATH, id="configuration_documentation_path")
            else:
                yield FilteredDirectoryTree(HOME_PATH, id="configuration_documentation_path")
            yield Label("Path selected:", classes="format_selection", shrink=True)
            yield Input(id="input_documentation_path", disabled=True)
            yield Horizontal(Button("Quit", variant="error"), Button("Confirm Path", variant="success", id="confirm_path_doc"), id="select_path_doc_horizontal")
            
        
    
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

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        if not self.only_directories:
            tree_id = event.control.id
            if tree_id == "configuration_documentation_path":
                self.query_one("#input_documentation_path", Input).value = str(event.path)
            logger.info(__name__, f"File selected: {str(event.path)}")

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
            Select(((line, line) for line in METHOD_LINES), id="select_method", value="Quick (ChatGPT-3.5)"),
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
                self.app.push_screen(Loader("Working on your documentation!"))
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

class MigrationDocGenerator(Screen):
    current_language = None

    def compose(self):
        yield Vertical(
            Label(
                "Select the programming language of your project:",
                classes="format_selection",
                shrink=True,
            ),
            Select(
                ((line, line) for line in PROGRAMMING_LANGUAGE),
                id="select_language",
            ),
            Label(
                "Select the current language version and the language version that you want to migrate to:",
                classes="format_selection",
                shrink=True,
            ),
            Horizontal(
                Vertical(
                    Label(
                        "Current version",
                        classes="format_selection",
                        shrink=True,
                    ),
                    Select(
                        [],
                        id="select_current_lang",
                        disabled=True,
                    ),
                    classes="doc_generator_vertical",
                ),
                Vertical(
                    Label(
                        "Targer version",
                        classes="format_selection",
                        shrink=True,
                    ),
                    Select(
                        [],
                        id="select_target_lang",
                        disabled=True,
                    ),
                    classes="doc_generator_vertical",
                ),
                classes="doc_generator_horizontal",
            ),
            Label(
                "Select the path to save the document with the analysis (the current directory is taken by default):",
                classes="format_selection",
            ),
            Horizontal(
                Button("Select path", id="select_path_button"),
                Input(
                    id="input_doc_path",
                    disabled=True,
                    value=file_manager.get_folder_path(),
                ),
                classes="doc_generator_horizontal",
            ),
            Horizontal(
                Button("Quit", variant="error", id="quit_screen", classes="half_button"),
                Button(
                    "Create Migration Documentation",
                    variant="success",
                    id="generate_migration_doc",
                    classes="half_button",
                ),
                classes="doc_generator_horizontal",
            ),
            classes="dialog_doc",
        )
    
    def on_select_changed(self, event: Select.Changed) -> None:
        id = event.select.id
        select_current = self.query_one("#select_current_lang", Select)
        select_target = self.query_one("#select_target_lang", Select)
        if id == "select_language":
            if event.value == Select.BLANK:
                select_current.set_options([])
                select_current.disabled = True
                select_target.set_options([])
                select_target.disabled = True
                self.current_language = None
            elif self.current_language is None:
                select_current.set_options([(item, item) for item in LANGUAGE_VERSIONS[str(event.value)]])
                select_current.disabled = False
                self.current_language = event.value
            elif self.current_language != event.value:
                select_current.set_options([(item, item) for item in LANGUAGE_VERSIONS[str(event.value)]])
                select_target.set_options([])
                select_target.disabled = True
                self.current_language = event.value
            
        elif id == "select_current_lang":
            if event.value == Select.BLANK:
                select_target.set_options([])
                select_target.disabled = True
            else:
                select_target.set_options([(item, item) for item in LANGUAGE_VERSIONS[self.current_language] if item != str(event.value)])
                select_target.disabled = False
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """
            Called when the worker state changes.
        """
        logger.info(__name__, f"(on_worker_state_changed) Worker state changed with event: {str(event)}")
        if WorkerState.SUCCESS == event.worker.state and event.worker.name == "migrate_files":
            self.app.pop_screen()
            self.app.pop_screen()
            #self.dismiss("OK")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate_migration_doc":
            select_current = self.query_one("#select_current_lang", Select).value
            select_target = self.query_one("#select_target_lang", Select).value
            doc_path = self.query_one("#input_doc_path", Input).value
            if select_current != Select.BLANK and select_target != Select.BLANK and self.current_language is not None:
                self.app.push_screen(Loader("Working on the migration..."))
                self.run_worker(migrate_files(self.current_language, select_current, select_target, doc_path), exclusive=False, thread=True)
            elif self.current_language is None:
                self.notify("You must select a language.")
            else:
                self.notify("You must select a current language version and a target language version.")
        else:
            self.app.pop_screen()

class Loader(Screen):
    def __init__(self, text) -> None:
        self.text = text
        super().__init__()

    def compose(self):
        logger.info(__name__, "Composing DocLoader")
        yield Vertical(
            Label(self.text, id = "doc_title"),
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

class DocumentResultResume(Screen):
    def __init__(self, result) -> None:
        self.result = result
        self.result = [
            {
                "file": "filename1.py",
                "functions": 10,
                "total": 12,
                "errors": [
                ]
            }, 
            {
                "file": "filename2.py",
                "functions": 15,
                "total": 20,
                "errors": [
                    {
                        "funtion_name": "function1",
                        "error": "error1"
                    }, 
                                        {
                        "funtion_name": "function1",
                        "error": "error1"
                    }
                ]
            },
                        {
                "file": "filename2.py",
                "functions": 15,
                "total": 20,
                "errors": [
                    {
                        "funtion_name": "function1",
                        "error": "error1"
                    }, 
                                        {
                        "funtion_name": "function1",
                        "error": "error1"
                    }
                ]
            },  
        ]
        self.md_result = ""
        self.buildMD()
        super().__init__()

    def compose(self):
        with Vertical(classes="dialog_results"):
            with VerticalScroll(id="doc_result_scroll"):
                yield Markdown(self.md_result)
            yield Button("Save result", id="save_result_btn", variant="success", classes="dialog_btn")

    def buildMD(self):
        markdown_text = ""
        markdown_text += "# Documentation Results\n"

        for result in self.result:
            porcentage = (result['functions'] / result['total']) * 100
            if result['functions'] == result['total']:
                markdown_text += f"## {result['file']} was documented at {int(porcentage)}%\n"
                markdown_text += f"Funtions documentated {result['functions']}/{result['total']} \n"

            else:
                markdown_text += f"## {result['file']} was documented at {int(porcentage)}%\n"
                markdown_text += f"Funtions documentated {result['functions']}/{result['total']} \n"
            if len(result['errors']) > 0:
                markdown_text += f"### Errors:\n"
                for error in result['errors']:
                    markdown_text += f"- {error['funtion_name']}: {error['error']}\n"
        self.md_result = markdown_text
    
    def _on_mount(self, event: Mount) -> None:
        self.buildMD()

    def save_result_callback(self, path):
        logger.info(__name__, f"(save_result_callback) Path selected: {str(path)}")
        if path != "":
            try:
                with open(os.path.join(path, "result.md"), "w") as file:
                    file.write(self.md_result)
                self.app.notify(f"File saved at {path}")
                self.app.pop_screen()
            except Exception as e:
                pass


    def on_button_pressed(self, event: Button.Pressed):
        """
            Called when a button is pressed.
        """
        button_pressed =  event.button.id
        logger.info(__name__, f"(on_button_pressed) Button pressed: {button_pressed}")
        if button_pressed == "save_result_btn":
            self.app.push_screen(PathSelector(), self.save_result_callback)
