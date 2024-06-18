from textual.widgets import Static, TabbedContent, TabPane, Input, Label, Button, DirectoryTree
from fridacli.commands.subcommands.files_commands import open_subcommand, update_log_path
from fridacli.config import get_config_vars, write_config_to_file, get_vars_as_dict, HOME_PATH
from fridacli.gui.code_view import FilteredDirectoryTree
from textual.containers import Horizontal, Vertical
from fridacli.logger import Logger
from textual.events import Mount
from fridacli.chatbot import ChatbotAgent
from fridacli.config import OS
from fridacli.config import HOME_PATH, FRIDA_DIR_PATH
import subprocess
import os

chatbot = ChatbotAgent()

logger = Logger()

class ConfigurationView(Static):
    model_counter = 0  # Counter for model inputs

    def compose(self):
        logger.info(__name__, "(compose) Composing ConfigurationView")
        with TabbedContent(initial="project"):
            with TabPane("Project", id="project"):
                with Static():
                    yield Vertical(
                        Label("Project path", classes="configuration_label"),
                        FilteredDirectoryTree(HOME_PATH, id="configuration_directorytree_projectpath"),
                        Input(id="input_project_path"),
                        classes="configuration_vertical",
                    )
                    with Horizontal():
                        yield Button("Save configuration", id="btn_project_confirm")
                        yield Button("Open logs", id="btn_project_open_logs", variant="primary")
            with TabPane("Softtek", id="softtek"):
                with Static():
                    yield Horizontal(
                        Label("LLMOPS API KEY", classes="configuration_label"),
                        Input(id="input_llmops_api_key"),
                        classes="configuration_line",
                    )
                    yield Horizontal(
                        Button("ADD MODEL", id="btn_add_model"),
                        classes="configuration_add_model",
                        id="add_model"
                    )
                    yield Vertical(id="models_container")  # Container to hold model inputs
                    yield Button("Save configuration", id="btn_softtek_confirm")
            with TabPane("Python", id="python"):
                with Static():
                    yield Vertical(
                        Label("Python ENV", classes="configuration_label"),
                        FilteredDirectoryTree(HOME_PATH, id="configuration_directorytree_pythonenv"),
                        Input(id="input_python_env"),
                        classes="configuration_vertical",
                    )
                    yield Button("Save configuration", id="btn_python_confirm")

    def _on_mount(self, event: Mount):
        """
        Update the inputs with the data in the configuration file
        """
        logger.info(__name__, "(on_mount) Mounting ConfigurationView")
        env_vars = get_config_vars()
        input_project_path = self.query_one("#input_project_path", Input)
        input_llmops_api_key = self.query_one("#input_llmops_api_key", Input)
        input_python_env = self.query_one("#input_python_env", Input)

        input_project_path.value = env_vars["PROJECT_PATH"]
        input_llmops_api_key.value = env_vars["LLMOPS_API_KEY"]
        input_python_env.value = env_vars["PYTHON_ENV_PATH"]

        # Get model count
        self.model_counter = int(env_vars.get("MODEL_COUNT", 0))

        # Load models
        models_container = self.query_one("#models_container", Vertical)
        for i in range(self.model_counter):
            self.add_model_input(models_container, i + 1, env_vars.get(f"MODEL_{i+1}", ""))

        logger.info(__name__, f"""(on_mount) 
            input_project_path: {input_project_path.value}
            input_llmops_api_key: {input_llmops_api_key.value}
            input_python_env: {input_python_env.value}          
        """)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Update the configuration file
        """
        button_pressed = str(event.button.id)
        logger.info(__name__, f"(on_button_pressed) Button pressed: {button_pressed}")
        if button_pressed == "btn_project_confirm":
            project_path = self.query_one("#input_project_path", Input).value

            if not project_path:
                self.notify("Please fill project path")
                return

            keys = get_vars_as_dict()
            keys["PROJECT_PATH"] = project_path
            write_config_to_file(keys)
            open_subcommand(keys["PROJECT_PATH"])
            self.parent.parent.query_one("#cv_tree_view", FilteredDirectoryTree).remove()
            self.parent.parent.query_one("#code_view_left", Vertical).mount(
                FilteredDirectoryTree(str(keys["PROJECT_PATH"]), id="cv_tree_view")
            )
            #code_view.refresh(repaint=True)
            self.notify("The configuration were saved")

        elif button_pressed == "btn_project_open_logs":
            if OS == "win":
                os.startfile(os.path.join(FRIDA_DIR_PATH, "fridacli_logs/"))
            else:
                subprocess.call(('open', os.path.join(FRIDA_DIR_PATH, "fridacli_logs/")))

        elif button_pressed == "btn_add_model":
            models_container = self.query_one("#models_container", Vertical)
            self.model_counter += 1
            self.add_model_input(models_container, self.model_counter)
            self.notify("Model added")

        elif button_pressed.startswith("btn_remove_model_"):
            model_number = int(button_pressed.split("_")[-1])
            self.remove_model_input(model_number)

        elif button_pressed == "btn_softtek_confirm":
            keys = get_vars_as_dict()
            value = self.query_one("#input_llmops_api_key", Input).value
            if not value:
                self.notify("Please fill LLMOPS API KEY", severity="error")
                return
            keys["LLMOPS_API_KEY"] = value

            # Save model inputs
            models_container = self.query_one("#models_container", Vertical)
            model_inputs = models_container.query(Input)
            keys["MODEL_COUNT"] = str(len(model_inputs))
            for i, input_field in enumerate(model_inputs):
                keys[f"MODEL_{i+1}"] = input_field.value

            write_config_to_file(keys)
            chatbot.update_env_vars()
            self.notify("The configuration were saved")

        elif button_pressed == "btn_python_confirm":
            keys = get_vars_as_dict()
            value = self.query_one("#input_python_env", Input).value
            keys["PYTHON_ENV_PATH"] = value
            write_config_to_file(keys)
            self.notify("The configuration were saved")

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        """
            Update the input with the selected directory
        """
        logger.info(__name__, f"(on_directory_tree_directory_selected) Directory selected: {str(event.path)}")
        tree_id = event.control.id
        if tree_id == "configuration_directorytree_projectpath":
            self.query_one("#input_project_path", Input).value = str(event.path)
        else: 
            self.query_one("#input_python_env", Input).value = str(event.path)

    def add_model_input(self, container, model_number, model_value=""):
        container.mount(
            Horizontal(
                Label(f"Model {model_number}", classes="configuration_label"),
                Input(value=model_value, id=f"input_model_{model_number}"),
                Button("Remove", id=f"btn_remove_model_{model_number}"),
                classes="configuration_line",
            ),
            before = self.parent.parent.query_one("#softtek", TabPane).query_one("#add_model", Horizontal)
        )

    def remove_model_input(self, model_number):
        models_container = self.query_one("#models_container", Vertical)
        model_to_remove = self.query_one(f"#input_model_{model_number}", Input).parent
        models_container.remove(model_to_remove)
        self.update_model_numbers()

    def update_model_numbers(self):
        models_container = self.query_one("#models_container", Vertical)
        model_inputs = models_container.query(Input)
        self.model_counter = len(model_inputs)
        for i, input_field in enumerate(model_inputs):
            label = input_field.parent.query_one(Label)
            label.update(f"Model {i + 1}")
            input_field.id = f"input_model_{i + 1}"
            remove_button = input_field.parent.query_one(Button)
            remove_button.id = f"btn_remove_model_{i + 1}"
