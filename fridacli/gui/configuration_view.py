from textual.widgets import Static, TabbedContent, TabPane, Input, Label, Button, DirectoryTree
from fridacli.commands.subcommands.files_commands import open_subcommand, update_log_path
from fridacli.config import get_config_vars, write_config_to_file, get_vars_as_dict, HOME_PATH
from fridacli.gui.code_view import FilteredDirectoryTree
from textual.containers import Horizontal, Vertical
from fridacli.logger import Logger
from textual.events import Mount
from fridacli.chatbot import ChatbotAgent
from fridacli.config import OS
from fridacli.config import HOME_PATH
import subprocess
import os

chatbot = ChatbotAgent()

logger = Logger()



class ConfigurationView(Static):
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
                        Label("CHAT MODEL NAME V3", classes="configuration_label"),
                        Input(id="input_chat_model_name"),
                        classes="configuration_line",
                    )
                    yield Horizontal(
                        Label("CHAT MODEL NAME V4", classes="configuration_label"),
                        Input(id="input_chat_model_name_v4"),
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
        logger.info(__name__, "(on_mount) Mounting ConfigurationView")
        env_vars = get_config_vars()
        input_project_path = self.query_one("#input_project_path", Input)
        input_llmops_api_key = self.query_one("#input_llmops_api_key", Input)
        input_chat_model_name = self.query_one("#input_chat_model_name", Input)
        input_chat_model_name_v4 = self.query_one("#input_chat_model_name_v4", Input)
        input_python_env = self.query_one("#input_python_env", Input)

        input_project_path.value = env_vars["PROJECT_PATH"]
        input_llmops_api_key.value = env_vars["LLMOPS_API_KEY"]
        input_chat_model_name.value = env_vars["CHAT_MODEL_NAME"]
        input_chat_model_name_v4.value = env_vars["CHAT_MODEL_NAME_V4"]
        input_python_env.value = env_vars["PYTHON_ENV_PATH"]

        logger.info(__name__, f"""(on_mount) 
            input_project_path: {input_project_path.value}
            input_llmops_api_key: {input_llmops_api_key.value}
            input_chat_model_name: {input_chat_model_name.value}
            input_chat_model_name_v4: {input_chat_model_name_v4.value} 
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
                self.notify("Please fill proje")
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
        if button_pressed == "btn_project_open_logs":
            if OS == "win":
                os.startfile(os.path.join(HOME_PATH, "fridacli_logs/"))
            else:
                subprocess.call(('open', os.path.join(HOME_PATH, "fridacli_logs/")))

        elif button_pressed == "btn_softtek_confirm":
            keys = get_vars_as_dict()
            value = self.query_one("#input_llmops_api_key", Input).value
            if not value:
                self.notify("Please fill LLMOPS API KEY", severity="error")
                return
            keys["LLMOPS_API_KEY"] = value

            value = self.query_one("#input_chat_model_name", Input).value
            if not value:
                self.notify("Please fill CHAT MODEL NAME V3", severity="error")
                return
            keys["CHAT_MODEL_NAME"] = value

            value = self.query_one("#input_chat_model_name_v4", Input).value
            if not value:
                self.notify("Please fill CHAT MODEL NAME V4", severity="error")
                return
            keys["CHAT_MODEL_NAME_V4"] = value
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
