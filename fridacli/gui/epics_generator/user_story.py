from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.widgets import  TextArea, RadioButton
from fridacli.logger import Logger

project_description = ""

logger = Logger()

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