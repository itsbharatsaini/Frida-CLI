from os import error
from textual.widgets import Static
from rich.text import Text
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.widgets import Label, TextArea, RadioButton
from textual.worker import Worker, WorkerState
from .utils import (
    create_empty_userstory,
    create_generated_user_story,
    complete_epic_cell,
    enhance_text
)
from .push_screens import NewObjectPushScreen
from .user_story import UserStory
from fridacli.logger import Logger
from fridacli.gui.push_screens import Loader

project_description = ""
logger = Logger()


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

    def __init__(self, epic, project_description) -> None:
        self.epic = epic
        self.userstories_names = []
        super().__init__()
        self.shrink = True
        self.expand = True
        self.selected = False
        self.project_description = project_description
        self.selected_text_area = None
        self.user_story_generated = {}
        self.completed_epic = {}

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
            #yield Button("Complete Cells", variant="success", id="complete_cell_btn")
            yield Button(":sparkles: Enhance or complete", id="enhance_btn", variant="primary")

    def update_user_stories(self, user_stories):
        """
            Updates the UserStory components based on the provided user stories.
        """
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        user_stories_component.remove_children(UserStory)
        for user_story in user_stories:
            logger.info(__name__, "user story: " + str(user_story))
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
        self.epic = {
            "epic_name": self.epic["epic_name"],
            "user_stories": user_stories_list
        }
        return self.epic

    def create_new_user_story(self, user_story):
        user_stories_component = self.query_one("#user_story_vertical", Vertical)
        user_stories_component.mount(UserStory(user_story))

    async def create_new_user_story_callback(self, result):
        """
            Callback function for creating a new user story. Creates a new UserStory 
            component with the generated user story based on the result.
            Called by NewObjectPushScreen when generate button is pressed.
        """
        is_empty, name = result
        self.user_story_generated = await create_generated_user_story(self.epic, name, is_empty, self.project_description)

    def build_user_story_callback(self, args):
        """
            Builds the user story after the callback is called.
            Called by NewObjectPushScreen when dismiss is called.
        """
        if self.user_story_generated != {}:
            self.create_new_user_story(self.user_story_generated)
        else:
            self.notify("An error occurred while creating the user story", severity="error")

    def is_selected(self):
        return self.selected
    
    async def enheance_text_callback(self):
        text = self.selected_text_area.text
        id = self.selected_text_area.id
        user_story_obj = self.selected_text_area.parent.parent
        logger.info(__name__, f"TextArea clicked parent: " + str(user_story_obj))
        if text == "":
            #Complete the cell when is empty
            enhanced_text = await complete_epic_cell(user_story_obj.user_story, id)
            self.selected_text_area.text = enhanced_text
        else:
            #Enhance the text    
            enhanced_text = await enhance_text(text, id)
            logger.info(__name__, f"Enhanced text: " + enhanced_text)
            self.selected_text_area.text = enhanced_text

    async def complete_epic_callback(self):
        #self.completed_epic = await complete_epic_cell(self.epic, project_description)
        pass

    def build_completed_epic_callback(self):
        if self.completed_epic != {}:
            self.update_user_stories(self.completed_epic["user_stories"])
        else:
            self.notify("An error occurred while completing the cells", severity="error")

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
            #self.complete_epic_callback()
            self.app.push_screen(Loader("Completing cells ..."))
            if self.selected_text_area != None:
                self.run_worker(self.complete_epic_callback(), exclusive=False, thread=True)
            else:
                self.notify("No text area selected", severity="error")

        elif button_pressed == "create_new_user_story_btn":
            # Create a new user story
            self.app.push_screen(NewObjectPushScreen("user story", self.create_new_user_story_callback), self.build_user_story_callback)
        elif button_pressed == "enhance_btn":
            if self.selected_text_area != None:
                loader_text = "Enhancing text :sparkles:..." if self.selected_text_area.text != "" else "Completing cell :sparkles:..."
                self.app.push_screen(Loader(loader_text))
                self.run_worker(self.enheance_text_callback(), exclusive=False, thread=True)
            else:
                self.notify("No text area selected", severity="error")

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
    
    def on_text_area_selection_changed(self, event: TextArea.SelectionChanged):
        self.selected_text_area = event.text_area
        logger.info(__name__, f"TextArea clicked: " + event.text_area.id)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        if WorkerState.SUCCESS == event.worker.state:
            if event.worker.name == "enheance_text_callback" or event.worker.name == "complete_epic_callback":
                self.app.pop_screen()
                #self.build_completed_epic_callback()
        logger.info(__name__, f"{event}")