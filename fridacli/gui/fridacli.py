from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, TabbedContent, TabPane, Label
from .chat_view import ChatView
from .code_view import CodeView
from fridacli.config import get_config_vars
from .configuration_view import ConfigurationView
from .first_time_config_view import FirstTimeConfiguration
from textual.screen import Screen

keys = get_config_vars()


class FridaCLI(App):
    CSS_PATH = "tcss/frida_styles.tcss"
    BINDINGS = [
        ("enter", "submit", "submit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        if keys["PROJECT_SETUP"] == "FALSE":
            self.app.push_screen(FirstTimeConfiguration(), self.first_time_config_callback)
        else:
            self.app.push_screen(PrincipalScreen())

    def first_time_config_callback(self, result):
        self.app.push_screen(PrincipalScreen())

class PrincipalScreen(Screen):
    def compose(self) -> ComposeResult:
        with TabbedContent(initial="frida_chat"):
            with TabPane("Configurations", id="configurations"):  # First tab
                # yield CodeView()
                yield ConfigurationView()
            with TabPane("Frida Chat", id="frida_chat"):  # First tab
                # yield CodeView()
                yield Horizontal(CodeView(id="code_view_pather"), ChatView())
            with TabPane("Code Snippets", id="code_snippets"):
                yield Label("Holaaa")