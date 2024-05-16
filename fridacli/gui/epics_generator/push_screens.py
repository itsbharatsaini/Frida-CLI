from logging import disable
from textual.screen import Screen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, Checkbox, RadioSet, RadioButton, TextArea
from textual.containers import Vertical, Horizontal
from fridacli.logger import Logger

logger = Logger()

class NewObjectPushScreen(Screen):
    radio_set_value = ""
    def __init__(self, title) -> None:
        super().__init__()
        self.title = title
        self.first_option = "Create empty " + str(self.title)
        self.second_option = "Create generated " + str(self.title)
    def compose(self):
        yield Vertical(
            Label("Create new " + str(self.title), id="platform_label"),
            RadioSet(
                RadioButton(self.first_option),
                RadioButton(self.second_option),
                id="platform_radio"
            ),
            Label(f"* Write the {self.title} name", classes="new_epic_push_components"),
            Input("", id="epic_name_input"),
            Horizontal(
                Button("Cancel", variant="error", id="create_epic_quit"),
                Button("Generate", variant="success", id="create_epic_generate")
            ),
            classes="dialog",
        )

    def on_radio_set_changed(self, event: RadioSet.Changed):
        # Update the value of the RadioSet selection
        self.radio_set_value = str(event.pressed.label)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_epic_quit":
            self.app.pop_screen()
        elif event.button.id == "create_epic_generate":
            # Create empty epic
            params = self.query_one("#epic_name_input", Input).value
            if self.radio_set_value != "":
                self.dismiss((self.radio_set_value == self.first_option, params))
            else:
                self.notify("No option selected", severity="error")
