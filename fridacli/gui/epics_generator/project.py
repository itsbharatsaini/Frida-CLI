from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.widgets import Label, TabbedContent, TextArea
from fridacli.gui.push_screens import ConfirmPushView
from textual.widgets import Static, Select, Button
from textual.worker import Worker, WorkerState
from .push_screens import NewObjectPushScreen
from fridacli.gui.push_screens import Loader
from textual.widgets import Static
from fridacli.logger import Logger
from .user_story import UserStory
from .utils import (
    get_versions_names,
    create_generated_epic,
    save_project,
    save_csv,
    enhance_project_description,
)
from .epic import Epic

project_description = ""

logger = Logger()

ROWS = [
    ("User Story", "Description", "Acceptance Criteria", "Out Of Scope"),
    (
        "User Registration",
        "As a user, I want to be able to register an account",
        "",
        "",
    ),
]

class Options(TabbedContent):
    """
       The Options class is a component that abstracts all the actions involving a project, such as changing the project description and creating a new Epic. It inherits from the TabbedContent class.

        Attributes:
        - BORDER_TITLE: A constant containing the title of the border.

        Methods:
        - __init__(self, project_description, epics): Constructor method to initialize the Options component.
        - compose(self): A generator method that yields different UI components to be rendered.
        - create_new_epics_callback(self, result): A method that handles the callback when creating a new epic.
        - on_button_pressed(self, event: Button.Pressed): A method that handles the logic when a button is pressed.
    """
    BORDER_TITLE = "Data Catalog"

    def __init__(self, project_description, epics) -> None:
        super().__init__()
        self.project_description = project_description
        self.epics = epics
        self.epic_generated = {}


    def compose(self):
        yield Button("Create New Epic", id="new_epic_btn")
        yield Label("Project description")
        yield TextArea(self.project_description, id="project_description_textarea")
        yield Button(" :sparkles: Enhance project description", id="enhance_description_btn", variant="primary")


    async def create_new_epics_callback(self, result):
        """
            Callback function for creating a new epic. Creates a new Epic 
            component with the generated epic based on the result.
            Called by NewObjectPushScreen when generate button is pressed.
        """
        is_empty, name = result
        self.epic_generated = await create_generated_epic(self.epics, name, is_empty, self.project_description)

    def build_new_epic_callback(self, result):
        if self.epic_generated != {}:
            self.parent.parent.parent.create_new_epic(self.epic_generated)
            self.epic_generated = {}
        else:
            self.notify("An error occurred while creating the epic", severity="error")

    def get_data(self):
        description_text_area = self.query_one("#project_description_textarea", TextArea)
        description = description_text_area.text
        return description
    
    async def enhance_project_description_callback(self):
        """
            Callback function for enhancing the project description. Enhances the project description
        """
        description_text_area = self.query_one("#project_description_textarea", TextArea)
        description = description_text_area.text
        enhenced_description = await enhance_project_description(description)
        description_text_area.text = enhenced_description
        self.project_description = enhenced_description

    """ Event handlers """

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        #Create a new Epic
        if button_pressed == "new_epic_btn":
            logger.info(__name__, "epic btn")
            self.app.push_screen(NewObjectPushScreen("epic",  self.create_new_epics_callback), self.build_new_epic_callback)
        elif button_pressed == "save_description_btn":
            description_text_area = self.query_one("#project_description_textarea", TextArea)
            description = description_text_area.text
        elif button_pressed == "enhance_description_btn":
            self.app.push_screen(Loader("Enhancing project description :sparkles:..."))
            self.run_worker(self.enhance_project_description_callback, exclusive=False, thread=True)


    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if WorkerState.SUCCESS == event.worker.state:
            if event.worker.name == "enhance_project_description_callback":
                self.app.pop_screen()
                self.enhance_project_description_callback()

class Project(Static):
    """
        Represents a Project component that lists all the Epics presented and displays various options.

        Args:
            path (str): The path of the project.
            project (dict): The project details.
            idx (int): The project index.

        Attributes:
            path (str): The path of the project.
            project (dict): The project details.
            version (str): The version of the project.
            idx (int): The project index.
            versions_names (list): The list of available version names.

        Methods:
            compose(): Generates the structure of the project component.
            get_data(): Retrieves the data of the project, including the epics and versions.
            on_mount(): Initializes the project component when mounted.
            populate_components(version_name: str): Populates the components of the project based on the provided version.
            save_project_description(description: str): Saves the project description.
            populate_epics(version: dict): Populates the epics based on the provided version.
            update_select_options(options: list, disabled: bool): Updates the options of the version select component.
            create_new_epic(epic: str = ""): Creates a new epic within the project.
            on_select_changed(event: Select.Changed): Event handler for the select component's change event.
            on_button_pressed(event: Button.Pressed): Event handler for the button component's press event.
        """

    versions_names = """Version 1
    Version 2
    Version 3
    """.splitlines()
    def __init__(self, path, project, idx, save_data_callback) -> None:
        super().__init__()
        self.path = path
        self.project = project
        self.project_description = project["project_description"]
        self.version = ""
        self.idx = idx
        self.save_data_callback = save_data_callback


    def compose(self):
        with Horizontal():
            with Vertical(id="epics_container"):
                with Horizontal(id = "epics_horizontal_buttons"):
                    yield Select(
                        options = [(line, line) for line in self.versions_names],
                        prompt="Version",
                        id="epics_select",
                        disabled=True
                    )
                    yield Button("Delete", id="epic_delete_btn", variant="error", disabled=True)
                    yield Button("Save", id="epic_save_btn", variant="success", disabled=False)
                    yield Button(":arrow_down: Download", id="epic_download_btn", variant="primary", disabled=True)

                yield VerticalScroll(id="epics_list")
            with Vertical(id="epics_options"):
                yield Options(
                    self.project["project_description"],
                    self.project["versions"][0] if self.version == "" else list(filter(lambda x: x["epic_name"], self.project["versions"]))[0]
                )

    def get_data(self):
        """
            Retrieves the data of the project, including the epics and versions.
        """
        epics_list_components = self.query_one("#epics_list", VerticalScroll)
        epics = epics_list_components.query(Epic)
        # TO DO: Return also the versions
        epics_list = []
        for epic in epics:
            epics_list.append(epic.get_data())

        self.project["project_description"] = self.query_one(Options).get_data()
        versions = self.project["versions"]

        # Update the epics list
        for version in versions:
            if version["version_name"] == self.version:
                version["epics"] = epics_list
                break
        aux_project = self.project
        aux_project["versions"] = versions
        
        return aux_project

    def populate_components(self, version_name):
        #Get the versions
        versions = get_versions_names(self.project)
        if version_name == "":
            self.update_select_options(versions, True)

        #Update buttons
        self.query_one("#epic_delete_btn", Button).disabled = False
        self.query_one("#epic_download_btn", Button).disabled = False
        version = {}
        if version_name == "":
            version = self.project["versions"][0]
            self.version = version["version_name"]
        else:
            self.project["versions"]
            version = list(filter(lambda x: x["version_name"] == version_name, self.project["versions"]))
            if len(version) > 0:
                version = version[0]
        self.populate_epics(version)

    def save_project_description(self, description):
        self.project["project_description"] = description
        save_project(self.path, self.project)

    def populate_epics(self, version):
        epics = version["epics"]
        for epic in epics:
            self.create_new_epic(epic)

    def update_select_options(self, options, disabled):
        """
            Updates the options of the version select component.
        """
        select = self.query_one("#epics_select", Select)
        new_options = [(line, line) for line in options]
        select.set_options(new_options)
        if disabled:
            select.disabled = False

    def create_new_epic(self, epic=""):
        """
            Creates a new epic within the project.
        """
        self.query_one("#epics_list", VerticalScroll).mount(Epic(epic, self.project_description))

    def delete_components_callback(self, params):
        epics = self.query(Epic)
        user_stories_selected = False
        epics_selected = False

        # Remove selected user stories
        for epic in epics:
            user_stories = epic.query(UserStory)
            for user_story in user_stories:
                if user_story.is_selected():
                    user_story.remove()
                    user_stories_selected = True
            if epic.is_selected():
                epics_selected = True
                epic.remove()

        # Remove selected epics
        if not user_stories_selected:
            self.notify("No user stories selected", severity="error")
        if user_stories_selected or epics_selected:
            self.save_data_callback()
            self.notify("User stories deleted", severity="success")

    """ Event handlers """

    def on_mount(self):
        self.populate_components("")

    def on_select_changed(self, event: Select.Changed):
        """
            Event handler for the select component's change event.
        """
        version_selected = event.value
        self.query_one("#epics_list", VerticalScroll).remove_children("*")
        self.populate_components(version_selected)

    def on_button_pressed(self, event: Button.Pressed):
        """
            Event handler for the button component's press event.
        """
        button_pressed = str(event.button.id)
        if button_pressed == "epic_download_btn":
            # Save the project in a CSV file
            versions = self.project["versions"]
            for version in versions:
                if version["version_name"] == self.version:
                    status = save_csv(f"{self.project['project_name']}.csv", version)
                    # Notify the user
                    if status:
                        self.notify("The project CSV file was created")
                    else:
                        self.notify("Some error creating CSV file")

        elif button_pressed == "epic_save_btn":
            self.save_data_callback()

        elif button_pressed == "epic_delete_btn":
            # Remove selected epics and user stories
            self.app.push_screen(ConfirmPushView("Are you sure want to delete the components?"), self.delete_components_callback)
