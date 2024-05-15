from textual.screen import Screen
from textual.widgets import Static
from rich.text import Text
from textual.widgets import DirectoryTree, Static, Select, Button
from textual.containers import Vertical, Horizontal, VerticalScroll, Grid
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label, TabbedContent, TextArea
from fridacli.logger import Logger
from textual.binding import Binding
from .utils import (
    get_versions_names,
    create_empty_userstory,
    create_generated_epic,
    create_empty_epic,
    create_generated_user_story,
    save_project
)
from .push_screens import NewObjectPushScreen

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
    def __init__(self, user_story) -> None:
        super().__init__()
        self.user_story = user_story

    def compose(self):
        with Horizontal(classes="user_story_horizontal"):
            yield TextArea(self.user_story["user_story"], classes="user_story_textarea", id="userstory_name")
            yield TextArea(self.user_story["description"], classes="user_story_textarea", id="userstory_description")
            yield TextArea(
                self.user_story["acceptance_criteria"],
                classes="user_story_textarea",
                id="userstory_acceptance_criteria"
            )
            yield TextArea(self.user_story["out_of_scope"], classes="user_story_textarea", id="userstory_out_of_scope")

    def complete_cell(self):
        username_name = self.query_one("#userstory_name", TextArea)
        userstory_description = self.query_one("#userstory_description", TextArea)
        userstory_acceptance_criteria = self.query_one(
            "#userstory_acceptance_criteria", TextArea
        )
        userstory_out_of_scope = self.query_one("#userstory_out_of_scope", TextArea)

        username_name.value

    async def on_focus_in(self, event):
        logger.info(__name__, f"TextArea gained focus")


class Epic(Static):
    def __init__(self, epic) -> None:
        self.epic = epic
        self.userstories_names = []
        super().__init__()
        self.shrink = True
        self.expand = True

    def compose(self):
        yield Label(Text(self.epic["epic_name"], style="font-size: 30"), id="epic_label")
        with Horizontal(classes="user_story_horizontal_title"):
            yield TextArea("User story", classes="user_story_textarea_title", disabled=True)
            yield TextArea("Description", classes="user_story_textarea_title", disabled=True)
            yield TextArea("Acceptance Criteria", classes="user_story_textarea_title", disabled=True)
            yield TextArea("Out of Scope", classes="user_story_textarea_title", disabled=True)

        yield Vertical(classes="user_story_vertical", id="user_story_vertical")
        with Horizontal(classes="user_story_horizontal"):
            yield Button("Create New User Story", id="create_new_user_story_btn")
            yield Button("Complete Cells", variant="success")

    def on_mount(self):
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        for user_story in self.epic["user_stories"]:
            user_stories_component.mount(UserStory(user_story))

    def create_new_user_story(self, user_story):
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        user_stories_component.mount(UserStory(user_story))

    def create_new_user_story_callback(self, result):
        logger.info(__name__, result)
        is_empty, name = result
        user_story = create_generated_user_story(self.epic, name, is_empty)
        self.create_new_user_story(user_story)


    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        vertical = self.query_one("#user_story_vertical", Vertical)
        if button_pressed == "new_epic_btn":
            empty_userstory = create_empty_userstory()
            vertical.mount(UserStory(empty_userstory))

        elif button_pressed == "create_new_user_story_btn":
            self.app.push_screen(NewObjectPushScreen("user story"), self.create_new_user_story_callback)

    def create_new_userstory(self):
        #new_userstory = create_new_userstory_from_epic(self.epic_name, "Mobile app to sell computers", [])
        #logger.info(__name__, new_userstory)
        pass



class Options(TabbedContent):
    BORDER_TITLE = "Data Catalog"

    def __init__(self, project_drescription, epics) -> None:
        super().__init__()
        self.project_drescription = project_drescription
        self.epics = epics


    def compose(self):
        yield Button("Create New Epic", id="new_epic_btn")
        yield Label("Project description")
        yield TextArea(self.project_drescription, id="project_description_textarea")
        yield Button("Save description", id="save_description_btn")

    def create_new_epics_callback(self, result):
        #Create new epic from Chat
        is_empty, name = result

        user_story = create_generated_epic(self.epics, name, is_empty)
        self.parent.parent.parent.create_new_epic(user_story)

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
    versions_names = """Version 1
    Version 2
    Version 3
    """.splitlines()
    def __init__(self, path, project, idx) -> None:
        super().__init__()
        self.path = path
        self.project = project
        self.version = ""
        self.idx = idx
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
                    yield Button("Edit", id="epic_edit_btn", disabled=True)
                    yield Button("Download", id="epic_download_btn", disabled=True)

                yield VerticalScroll(id="epics_list")
            with Vertical(id="epics_options"):
                yield Options(
                    self.project["project_description"],
                    self.project["versions"][0] if self.version == "" else list(filter(lambda x: x["epic_name"], self.project["versions"]))[0]
                )

    def on_mount(self):
        self.populate_components("")

    def populate_components(self, version_name):
        #Get the versions
        versions = get_versions_names(self.project)
        if version_name == "":
            self.update_select_options(versions, True)

        #Update buttons
        self.query_one("#epic_edit_btn", Button).disabled = False
        self.query_one("#epic_download_btn", Button).disabled = False
        version = {}
        if version_name == "":
            version = self.project["versions"][0]
            self.version = version
        else:
            self.project["versions"]
            version = list(filter(lambda x: x["version_name"] == version_name, self.project["versions"]))
            if len(version) > 0:
                version = version[0]
        logger.info(__name__,"version " + str(version))
        self.populate_epics(version)

    def save_project_description(self, description):
        self.project["project_description"] = description
        save_project(self.path, self.project)

    def populate_epics(self, version):
        epics = version["epics"]
        for epic in epics:
            self.create_new_epic(epic)

    def update_select_options(self, options, disabled):
        select = self.query_one("#epics_select", Select)
        new_options = [(line, line) for line in options]
        select.set_options(new_options)
        if disabled:
            select.disabled = False

    def create_new_epic(self, epic=""):
        self.query_one("#epics_list", VerticalScroll).mount(Epic(epic))

    def on_select_changed(self, event: Select.Changed):
        logger.info(__name__, "clicked")
        version_selected = event.value
        self.query_one("#epics_list", VerticalScroll).remove_children("*")
        self.populate_components(version_selected)
