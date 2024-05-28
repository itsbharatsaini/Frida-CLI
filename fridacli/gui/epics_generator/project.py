from os import error
from textual.screen import Screen
from textual.widgets import Static
from rich.text import Text
from textual.widgets import DirectoryTree, Static, Select, Button
from textual.containers import Vertical, Horizontal, VerticalScroll, Grid
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label, TabbedContent, TextArea, RadioButton
from fridacli.logger import Logger
from textual.binding import Binding
from .utils import (
    get_versions_names,
    create_empty_userstory,
    create_generated_epic,
    create_empty_epic,
    create_generated_user_story,
    save_project,
    complete_epic,
    save_csv
)
from .push_screens import NewObjectPushScreen
from fridacli.gui.push_screens import ConfirmPushView

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


class UserStory(Static):
    """
        A class representing a user story in a horizontal layout.
        Args:
            user_story (dict): The user story data.

        Methods:
            compose(): Composes and yields the elements of the user story in a horizontal layout.
            get_data(): Gets the text data from the TextArea elements.
            complete_cell(): Retrieves the value from the username_name TextArea.
            on_button_pressed(event: Button.Pressed): Handles the event when a button is pressed.
            on_text_area_pressed(event): Handles the event when a TextArea gains focus.
    """
    def __init__(self, user_story) -> None:
        super().__init__()
        self.user_story = user_story
        self.selected = False

    def compose(self):
        with Horizontal(classes="user_story_horizontal"):
            yield Vertical(
                RadioButton("", classes="user_story_del_btn", id="user_story_del_btn"),
                id="vertical_del_button"
            )
            yield TextArea(self.user_story["user_story"], classes="user_story_textarea", id="userstory_name")
            yield TextArea(self.user_story["description"], classes="user_story_textarea", id="userstory_description")
            yield TextArea(
                self.user_story["acceptance_criteria"],
                classes="user_story_textarea",
                id="userstory_acceptance_criteria"
            )
            yield TextArea(self.user_story["out_of_scope"], classes="user_story_textarea", id="userstory_out_of_scope")


    def get_data(self):
        #return the text in the TextAreas
        user_story = self.query_one("#userstory_name", TextArea).text
        description = self.query_one("#userstory_description", TextArea).text
        acceptance_criteria = self.query_one("#userstory_acceptance_criteria", TextArea).text
        out_of_scope = self.query_one("#userstory_out_of_scope").text
        return {
            "user_story": user_story,
            "description": description,
            "acceptance_criteria": acceptance_criteria,
            "out_of_scope": out_of_scope
        }


    def complete_cell(self):
        """
            Retrieves the value from the username_name TextArea.
        """
        username_name = self.query_one("#userstory_name", TextArea)
        userstory_description = self.query_one("#userstory_description", TextArea)
        userstory_acceptance_criteria = self.query_one(
            "#userstory_acceptance_criteria", TextArea
        )
        userstory_out_of_scope = self.query_one("#userstory_out_of_scope", TextArea)

        username_name.value

    def change_radiobutton_to_checked(self, value):
        self.selected = value
        radio_buttons = self.query(RadioButton)
        for radio_button in radio_buttons:
            radio_button.value = value

    def is_selected(self):
        return self.selected

    """
        Event handlers
    """
    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        if button_pressed == "vertical_del_button":
            logger.info(__name__, "p")

    def on_text_area_pressed(self, event):
        logger.info(__name__, f"TextArea gained focus")


    def on_radio_button_changed(self, event: RadioButton.Changed):
        self.selected = event.radio_button.value



class Epic(Static):
    """
        Class representing an Epic, which abstracts the Epic and contains functionality related to managing user stories within the Epic.

        Attributes:
            epic (any): The Epic object.
        Methods:
            init(epic: any) -> None: Initializes the Epic instance with the given epic object.
            compose() -> Generator: Yields the UI components required to display the Epic and user stories.
            on_mount() -> None: Mounts the UserStory components for each user story in the Epic.
            update_user_stories(user_stories: List[any]) -> None: Updates the UserStory components based on the provided user stories.
            get_data() -> Dict[str, any]: Returns the data of the Epic and user stories.
            create_new_user_story(user_story: any) -> None: Creates a new UserStory component with the provided user story and mounts it.
            create_new_user_story_callback(result: Tuple[bool, str]) -> None: Callback function for creating a new user story. Creates a new UserStory component with the generated user story based on the result.
            on_button_pressed(event: Button.Pressed) -> None: Event handler for button presses. Handles creating a new user story, completing the Epic, and creating an empty user story.
    """

    def __init__(self, epic) -> None:
        self.epic = epic
        self.userstories_names = []
        super().__init__()
        self.shrink = True
        self.expand = True
        self.selected = False

    def compose(self):
        with Horizontal(classes = "epic_title_horizontal"):
            yield RadioButton("", classes="epic_del_btn", id="epic_del_btn")
            yield Label(Text(self.epic["epic_name"], style="font-size: 30"), classes="epic_label")

        with Horizontal(classes="user_story_horizontal_title"):
            yield TextArea("User story", classes="user_story_textarea_title_f", disabled=True)
            yield TextArea("Description", classes="user_story_textarea_title", disabled=True)
            yield TextArea("Acceptance Criteria", classes="user_story_textarea_title", disabled=True)
            yield TextArea("Out of Scope", classes="user_story_textarea_title", disabled=True)

        yield Vertical(classes="user_story_vertical", id="user_story_vertical")

        with Horizontal(classes="user_story_horizontal_btns"):
            yield Button("Create New User Story", id="create_new_user_story_btn")
            yield Button("Complete Cells", variant="success", id="complete_cell_btn")

    def update_user_stories(self, user_stories):
        """
            Updates the UserStory components based on the provided user stories.
        """
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        user_stories_component.remove_children(UserStory)
        for user_story in user_stories:
            user_stories_component.mount(UserStory(user_story))

    def get_data(self):
        """
            Returns the data of the Epic and user stories.
        """
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        user_stories = user_stories_component.query(UserStory)
        user_stories_list = []

        for user_story in user_stories:
            user_stories_list.append(user_story.get_data())

        return {
            "epic_name": self.epic["epic_name"],
            "user_stories": user_stories_list
        }

    def create_new_user_story(self, user_story):
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        user_stories_component.mount(UserStory(user_story))

    def create_new_user_story_callback(self, result):
        is_empty, name = result
        user_story = create_generated_user_story(self.epic, name, is_empty)
        self.create_new_user_story(user_story)

    def is_selected(self):
        return self.selected

    """ Event handlers """

    def on_mount(self):
        """
            Mounts the UserStory components for each user story in the Epic.
        """
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        for user_story in self.epic["user_stories"]:
            user_stories_component.mount(UserStory(user_story))

    def on_button_pressed(self, event: Button.Pressed):
        """
            Event handler for button presses. Handles creating a new user story,
            completing the Epic, and creating an empty user story.
            """
        button_pressed = str(event.button.id)
        vertical = self.query_one("#user_story_vertical", Vertical)
        if button_pressed == "new_epic_btn":
            # Create an empty user story
            empty_userstory = create_empty_userstory()
            vertical.mount(UserStory(empty_userstory))

        elif button_pressed == "complete_cell_btn":
            # Complete the empty cells
            response = complete_epic(self.epic, project_description)
            if response != None:
                self.update_user_stories(response["user_stories"])
                logger.info(__name__, str(response))

        elif button_pressed == "create_new_user_story_btn":
            # Create a new user story
            self.app.push_screen(NewObjectPushScreen("user story"), self.create_new_user_story_callback)

    def on_radio_button_changed(self, event: RadioButton.Changed):
        """
            Handles the event when a RadioButton is changed. Changes the state of the
            RadioButton and updates the user stories accordingly.
        """
        if event.radio_button.id == "epic_del_btn":
            self.selected = not self.selected
            user_stories = self.query(UserStory)
            for user_story in user_stories:
                user_story.change_radiobutton_to_checked(self.selected)

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

    def __init__(self, project_drescription, epics) -> None:
        super().__init__()
        self.project_drescription = project_drescription
        self.epics = epics


    def compose(self):
        yield Button("Create New Epic", id="new_epic_btn")
        yield Label("Project description")
        yield TextArea(self.project_drescription, id="project_description_textarea")


    def create_new_epics_callback(self, result):
        #Create new epic from Chat
        is_empty, name = result

        user_story = create_generated_epic(self.epics, name, is_empty)
        self.parent.parent.parent.create_new_epic(user_story)

    """ Event handlers """

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        #Create a new Epic
        if button_pressed == "new_epic_btn":
            logger.info(__name__, "epic btn")
            self.app.push_screen(NewObjectPushScreen("epic"), self.create_new_epics_callback)
        elif button_pressed == "save_description_btn":
            description_text_area = self.query_one("#project_description_textarea", TextArea)
            description = description_text_area.text
            #self.parent.save_project_description(description)



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
        project_description = project["project_description"]
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
        self.query_one("#epics_list", VerticalScroll).mount(Epic(epic))

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
