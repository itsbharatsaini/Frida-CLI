from textual.screen import Screen
from textual.widgets import Static
from rich.text import Text
from textual.widgets import DirectoryTree, Static, Select, Button
from textual.containers import Vertical, Horizontal, VerticalScroll, Grid
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label, TabbedContent, TextArea
from fridacli.logger import Logger
from textual.binding import Binding
#from fridacli.commands.recipes import create_new_userstory_from_epic

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
    def __init__(self,userstory_name) -> None:
        super().__init__()
        self.userstory_name = userstory_name

    def compose(self):
        with Horizontal(classes="user_story_horizontal"):
            yield TextArea(classes="user_story_textarea", id="userstory_name")
            yield TextArea(classes="user_story_textarea", id="userstory_description")
            yield TextArea(
                classes="user_story_textarea", id="userstory_acceptance_criteria"
            )
            yield TextArea(classes="user_story_textarea", id="userstory_out_of_scope")

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
    def __init__(self,epic_name) -> None:
        self.epic_name = epic_name
        self.userstories_names = []
        super().__init__(
            renderable,
            expand=True,
            shrink=True,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.shrink = True
        self.expand = True

    def compose(self) -> ComposeResult:
        yield Label(Text(self.epic_name, style="font-size: 30px"), id="epic_label")
        with Vertical(classes="user_story_vertical", id="user_story_vertical"):
            yield UserStory("")
            yield UserStory("")
        with Horizontal(classes="user_story_horizontal"):
            yield Button("Create New User Story", id="new_epic_btn")
            yield Button("Complete Cells", variant="success")

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        vertical = self.query_one("#user_story_vertical", Vertical)
        if button_pressed == "new_epic_btn":
            vertical.mount(UserStory(userstory_name = ""))
        else:
            self.create_new_userstory()

    def create_new_userstory(self):
        #new_userstory = create_new_userstory_from_epic(self.epic_name, "Mobile app to sell computers", [])
        #logger.info(__name__, new_userstory)
        pass



class Options(TabbedContent):
    BORDER_TITLE = "Data Catalog"

    def compose(self):
        yield Button("Create New Epic", id="new_epic_btn")
        yield Label("Project description")
        yield TextArea(id="project_description_textarea")

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        if button_pressed == "new_epic_btn":
            logger.info(__name__, self.parent.parent.parent)
            self.parent.parent.parent.create_new_epic("Test3")

class Project(Static):
    def compose(self):
        with Horizontal():
            with VerticalScroll(id="epics_list"):
                yield Epic(epic_name="Cart")
            with Vertical(id="epics_options"):
                yield Options()

    def create_new_epic(self, epic=""):
        self.query_one("#epics_list", VerticalScroll).mount(Epic(epic_name=epic))
