from logging import disable
from textual.screen import Screen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, RadioSet, RadioButton, TextArea
from textual.containers import Vertical, Horizontal
from fridacli.logger import Logger
from fridacli.gui.push_screens import PathSelector, Loader
from fridacli.config import HOME_PATH
from textual.worker import Worker, WorkerState
import csv 

logger = Logger()

class NewObjectPushScreen(Screen):
    radio_set_value = ""
    def __init__(self, title, callback) -> None:
        super().__init__()
        self.title = title
        self.callback = callback
        self.first_option = "Create empty " + str(self.title)
        self.second_option = "Create generated " + str(self.title)
    
    def compose(self):
        with Vertical(classes="new_object_dialog", id="new_object_vertical"):
            yield Label("Create new " + str(self.title), id="platform_label")
            yield RadioSet(
                RadioButton(self.first_option),
                RadioButton(self.second_option),
                id="platform_radio"
            )
            yield Label(f"* Write the {self.title} name", classes="new_epic_push_components")
            yield Input("", id="epic_name_input")
            yield Horizontal(
                Button("Cancel", variant="error", id="create_epic_quit"),
                Button("Generate", variant="success", id="create_epic_generate"),
            )
            yield Horizontal(id="new_object_horizontal")
            


    def on_radio_set_changed(self, event: RadioSet.Changed):
        # Update the value of the RadioSet selection
        self.radio_set_value = str(event.pressed.label)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_epic_quit":
            self.app.pop_screen()
        elif event.button.id == "create_epic_generate":
            # Create empty epic
            params = self.query_one("#epic_name_input", Input).value

            if self.radio_set_value != "":
                vertical = self.query_one("#new_object_horizontal", Horizontal)
                vertical.mount(LoadingIndicator())
                self.run_worker(
                    self.callback((self.radio_set_value == self.first_option, params)), 
                    exclusive=False,
                    thread=True, 
                    name="new_object_push_screen"
                )
                #self.app.push_screen(Loader("Generating..."))

                #self.dismiss((self.radio_set_value == self.first_option, params))
            else:
                self.notify("No option selected", severity="error")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if WorkerState.SUCCESS == event.worker.state:
            if event.worker.name == "new_object_push_screen":
                #self.app.pop_screen()
                self.dismiss("OK")
        logger.info(__name__, f"{event}")

class CreateNewProject(Screen):
    path = HOME_PATH
    radio_set_value = ""
    csv_data = {}
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

    def get_data_from_csv(self, path):
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
            return epics
        except Exception as e:
            logger.info(__name__, "Error while trying to get the data from the CSV file: " + str(e))
            return {}
        
    def upload_excel_callback(self, path):
        logger.info(__name__, "path: " + str(path))
        csv_data = self.get_data_from_csv(path)
        if csv_data != {}:
            self.csv_data = csv_data
            self.notify("CSV data retrived successfully")
        else:
            self.notify("An error occurred while trying to get the data from the CSV file", severity="error")
        logger.info(__name__, "data from csv" + str(self.csv_data))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_pressed = event.button.id
        if button_pressed == "create_epic_quit":
            self.app.pop_screen()
        elif button_pressed == "create_epic_generate":
            epic_name_input = self.query_one("#epic_name_input", Input).value
            plataform = str(self.radio_set_value)
            project_context_input = self.query_one("#project_context_input", TextArea).text
            if len(epic_name_input) > 0  and len(plataform) > 0 and len(project_context_input) > 0:
                params = {"epic_name": epic_name_input, "plataform": plataform, "project_description": project_context_input}
                if self.csv_data != {}:
                    params["csv_data"] = self.csv_data
                #params = (epic_name_input, plataform, project_context_input)
                self.dismiss(params)
            else:
                self.notify("Some of the values are empty", severity="error")
        elif button_pressed == "upload_excel_button":
            self.app.push_screen(PathSelector(only_directories=False, allow_special=False), self.upload_excel_callback)
            
