from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Header, TabbedContent, TabPane, Label
from .chat_view import ChatView
from .code_view import CodeView
from .configuration_view import ConfigurationView
from .epics_generator.epics_generation import EpicsGeneration
from fridacli.logger import Logger

logger = Logger()

class FridaCLI(App):
    CSS_PATH = "tcss/frida_styles.tcss"
    BINDINGS = [
        ("enter", "submit", "submit"),
    ]

    def compose(self) -> ComposeResult:
        logger.info(__name__, "Composing FridaCLI")
        yield Header()
        with TabbedContent(initial="frida_chat"):
            with TabPane("Configurations", id="configurations"):  # First tab
                yield ConfigurationView()
            with TabPane("Frida Chat", id="frida_chat"):  # First tab
                yield Horizontal(CodeView(id="code_view_pather"), ChatView(id="chat_view"))
            with TabPane("Epics Generation", id="epics_generation"):
                yield EpicsGeneration()
