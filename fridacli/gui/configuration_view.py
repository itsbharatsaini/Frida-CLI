from textual.widgets import Static, TabbedContent, TabPane, Input, Label, Button, DirectoryTree
from fridacli.commands.subcommands.files_commands import open_subcommand, update_log_path
from fridacli.config import get_config_vars, write_config_to_file, get_vars_as_dict, HOME_PATH
from fridacli.gui.code_view import FilteredDirectoryTree
from textual.containers import Horizontal, Vertical
from fridacli.logger import Logger
from textual.events import Mount
from typing import Iterable
from pathlib import Path

logger = Logger()



class ConfigurationView(Static):
    def compose(self):
        with TabbedContent(initial="project"):
            with TabPane("Project", id="project"):
                with Static():
                    yield Vertical(
                        Label("Project path", classes="configuration_label"),
                        FilteredDirectoryTree(HOME_PATH, id="configuration_directorytree_projectpath"),
                        Input(id="input_project_path"),
                        classes="configuration_vertical",
                    )
                    yield Horizontal(
                        Label("Logs path", classes="configuration_label"),
                        Input(id="input_logs_path"),
                        classes="configuration_line",
                    )
                    yield Button("Save configuration", id="btn_project_confirm")
            with TabPane("Softtek", id="softtek"):
                with Static():
                    yield Horizontal(
                        Label("LLMOPS API KEY", classes="configuration_label"),
                        Input(id="input_llmops_api_key"),
                        classes="configuration_line",
                    )
                    yield Horizontal(
                        Label("CHAT_MODEL_NAME", classes="configuration_label"),
                        Input(id="input_chat_model_name"),
                        classes="configuration_line",
                    )
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

        env_vars = get_config_vars()
        input_project_path = self.query_one("#input_project_path", Input)
        input_logs_path = self.query_one("#input_logs_path", Input)
        input_llmops_api_key = self.query_one("#input_llmops_api_key", Input)
        input_chat_model_name = self.query_one("#input_chat_model_name", Input)
        input_python_env = self.query_one("#input_python_env", Input)

        input_project_path.value = env_vars["PROJECT_PATH"]
        input_logs_path.value = env_vars["LOGS_PATH"]
        input_llmops_api_key.value = env_vars["LLMOPS_API_KEY"]
        input_chat_model_name.value = env_vars["CHAT_MODEL_NAME"]
        input_python_env.value = env_vars["PYTHON_ENV_PATH"]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Update the configuration file
        """
        button_pressed = str(event.button.id)
        if button_pressed == "btn_project_confirm":
            keys = get_vars_as_dict()
            keys["PROJECT_PATH"] = self.query_one("#input_project_path", Input).value
            keys["LOGS_PATH"] = self.query_one("#input_logs_path", Input).value
            write_config_to_file(keys)
            open_subcommand(keys["PROJECT_PATH"])
            update_log_path(keys["LOGS_PATH"])
            self.parent.parent.query_one("#cv_tree_view", FilteredDirectoryTree).remove()
            self.parent.parent.query_one("#code_view_left", Vertical).mount(FilteredDirectoryTree(str(keys["PROJECT_PATH"]), id="cv_tree_view"))
            #code_view.refresh(repaint=True)
            self.notify("The configuration were saved")

        elif button_pressed == "btn_softtek_confirm":
            keys = get_vars_as_dict()
            value = self.query_one("#input_llmops_api_key", Input).value
            keys["LLMOPS_API_KEY"] = value
            value = self.query_one("#input_chat_model_name", Input).value
            keys["CHAT_MODEL_NAME"] = value
            write_config_to_file(keys)
        elif button_pressed == "btn_python_confirm":
            keys = get_vars_as_dict()
            value = self.query_one("#input_python_env", Input).value
            keys["PYTHON_ENV_PATH"] = value
            write_config_to_file(keys)

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected):
        tree_id = event.control.id
        if tree_id == "configuration_directorytree_projectpath":
            self.query_one("#input_project_path", Input).value = str(event.path)
        else: 
            self.query_one("#input_python_env", Input).value = str(event.path)
