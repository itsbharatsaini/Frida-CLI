from textual.screen import Screen
from textual.widgets import Label, Input, Button, DirectoryTree, LoadingIndicator, Checkbox, RadioSet, RadioButton, TextArea
from textual.containers import Vertical, Horizontal

class NewProjectPushScreen(Screen):
    radio_set_value = ""
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_epic_quit":
            self.app.pop_screen()
        elif event.button.id == "create_epic_generate":
            epic_name_input = self.query_one("#epic_name_input", Input).value
            plataform = str(self.radio_set_value)
            project_context_input = self.query_one("#project_context_input", TextArea).text
            if len(epic_name_input) > 0  and len(plataform) > 0 and len(project_context_input) > 0:
                params = (epic_name_input, plataform, project_context_input)
                self.dismiss(params)
            else:
                self.notify("Some of the values are empty", severity="error")
