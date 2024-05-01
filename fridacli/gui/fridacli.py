from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, TabbedContent, TabPane, Label, Button
from .chat_view import ChatView
from .code_view import CodeView
from .configuration_view import ConfigurationView
from .create_epic_example_view import Create_epic_example


class FridaCLI(App):
    CSS_PATH = "tcss/frida_styles.tcss"
    BINDINGS = [
        ("enter", "submit", "submit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="frida_chat"):
            with TabPane("Configurations", id="configurations"):  # First tab
                # yield CodeView()
                yield ConfigurationView()
            with TabPane("Frida Chat", id="frida_chat"):  # First tab
                # yield CodeView()
                yield Horizontal(CodeView(id="code_view_pather"), ChatView())
            with TabPane("Code Snippets", id="code_snippets"):
                yield Label("Holaaa")
            with TabPane("Example", id="create_epic_test"):
                yield Create_epic_example()
