from textual.widgets import Input, Label, Button, DirectoryTree
from fridacli.gui.code_view import FilteredDirectoryTree
from fridacli.commands.subcommands.files_commands import open_subcommand, update_log_path
from fridacli.config import write_config_to_file, get_vars_as_dict, HOME_PATH
from textual.screen import Screen
from textual.containers import Horizontal, Vertical
from fridacli.logger import Logger

logger = Logger()

class FirstTimeConfiguration(Screen):
    def compose(self):
        yield Vertical(
            Label("WELCOME TO Frida CLI!"),
            Label("You must setup a few things before you can start using this tool."),
            Label("SOFTTEK SEPTUP"),
            Horizontal(
                Label("LLMOPS API KEY", classes="configuration_label"),
                Input(id="input_llmops_api_key"),
                classes="configuration_line",
            ),
            Horizontal(
                Label("CHAT_MODEL_NAME", classes="configuration_label"),
                Input(id="input_chat_model_name"),
                classes="configuration_line",
            ),
            Button("Save configuration", id="btn_softtek_confirm")
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Update the configuration file
        """
        button_pressed = str(event.button.id)
        if button_pressed == "btn_softtek_confirm":
            api_key = self.query_one("#input_llmops_api_key", Input).value
            model_name = self.query_one("#input_chat_model_name", Input).value

            if api_key == "" or model_name == "":
                self.notify(f"You must fill all the information required.")
            else:
                keys = get_vars_as_dict()
                keys["LLMOPS_API_KEY"] = api_key
                keys["CHAT_MODEL_NAME"] = model_name
                write_config_to_file(keys)
                self.app.push_screen(FirstProjectConfiguration(), self.first_project_config_callback)
    
    def first_project_config_callback(self, result):
        self.dismiss("OK")

class FirstProjectConfiguration(Screen):
    def compose(self):
        yield Vertical(
            Label("Now it's time to setup your first project."),
            Label("PROJECT SEPTUP"),
            Vertical(
                Label("PROJECT PATH", classes="configuration_label"),
                FilteredDirectoryTree(HOME_PATH, id="configuration_directorytree_projectpath"),
                Input(id="input_project_path"),
                classes="configuration_vertical",
            ),
            Horizontal(
                Label("LOGS PATH", classes="configuration_label"),
                Input(id="input_logs_path"),
                classes="configuration_line",
            ),
            Vertical(
                Label("ENV PATH", classes="configuration_label"),
                DirectoryTree(HOME_PATH, id="configuration_directorytree_pythonenv"),
                Input(id="input_python_env"),
                classes="configuration_vertical",
            ),
            Button("Save configuration", id="btn_project_confirm")
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Update the configuration file
        """
        button_pressed = str(event.button.id)
        if button_pressed == "btn_project_confirm":
            keys = get_vars_as_dict()
            project = self.query_one("#input_project_path", Input).value
            logs = self.query_one("#input_logs_path", Input).value
            env = self.query_one("#input_python_env", Input).value
            if project == "" or logs == "":
                self.notify("The project path and the logs path are mandatory.")
            else:
                keys["PROJECT_PATH"] = project
                keys["LOGS_PATH"] = logs
                keys["PROJECT_SETUP"] = "TRUE"
                if env != "":
                    keys["PYTHON_ENV_PATH"] = env
                write_config_to_file(keys)
                open_subcommand(keys["PROJECT_PATH"])
                update_log_path(keys["LOGS_PATH"])
                self.dismiss("OK")
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        tree_id = event.control.id
        if tree_id == "configuration_directorytree_projectpath":
            self.query_one("#input_project_path", Input).value = str(event.path)
        else: 
            self.query_one("#input_python_env", Input).value = str(event.path)