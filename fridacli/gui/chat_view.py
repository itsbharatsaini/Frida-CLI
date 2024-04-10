from .chat_responses.system_response import SystemUserResponse, SystemFridaResponse
from textual.containers import VerticalScroll, Vertical, HorizontalScroll
from .chat_responses.code_change_question import RunCodeConfirmation
from textual.widgets import Static, Input, Button
from fridacli.file_manager import FileManager
from fridacli.frida_coder import FridaCoder
from fridacli.chatbot import ChatbotAgent
from textual.app import ComposeResult
from rich.traceback import Traceback
from fridacli.logger import Logger
from textual.events import Mount
from rich.syntax import Syntax
from fridacli.config import OS

logger = Logger()


class ChatView(Static):
    chatbot_agent = ChatbotAgent()
    frida_coder = FridaCoder()
    file_manager = FileManager()
    mentioned_files = []
    chat_label_sz = 0

    CSS_PATH = "tcss/frida_styles.tcss"

    def compose(self) -> ComposeResult:
        with Vertical():
            with VerticalScroll(id="chat_scroll"):
                yield SystemFridaResponse(
                    "Hey there! Welcome to Frida, your go-to code buddy. Let's make coding awesome together!"
                )
            yield Input(id="input_chat")
            yield HorizontalScroll(id="cv_hs")

    def delete_child_cv_hs(self, file_name):
        """
        Delete children in the HorizontalScroll representing the files
        mentioned in the Input
        """
        id = self.mentioned_files.index(file_name)
        self.mentioned_files.remove(file_name)
        self.query_one("#cv_hs", HorizontalScroll).remove_children(
            f"#cv_hs_file_{id}"
        )

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        if len(message.value) < self.chat_label_sz:
            # If backspace is used to update the text
            tempo = self.mentioned_files.copy()

            for file in tempo:
                if file not in str(message.value):
                    logger.info(__name__, f"file_to_delete: {file}")
                    self.delete_child_cv_hs(file)
        else:
            self.chat_label_sz = len(message.value)
            paths = self.chatbot_agent.get_matching_files(
                message.value, self.mentioned_files
            )
            for path in paths:
                file_name = path.split("\\")[-1] if OS == "win" else path.split("/")[-1]
                logger.info(__name__, f"file_name: {file_name}")
                self.mentioned_files.append(file_name)
                id = len(self.mentioned_files) - 1
                self.query_one("#cv_hs", HorizontalScroll).mount(
                    Button(
                        str(file_name),
                        id=f"cv_hs_file_{id}",
                        classes="cv_hs_file_label",
                    )
                )
                self.display_code_file(path)

    def display_code_file(self, path):
        """Change and display the file that was mentioned"""
        code_view = self.parent.parent.query_one("#cv_code", Static)
        try:
            syntax = Syntax.from_path(
                str(path),
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme="github-dark",
                highlight_lines=[],
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.parent.parent.query_one("#cv_code_scroll").scroll_home(animate=False)
            self.sub_title = str(path)

    async def on_input_submitted(self):
        """Start the chat process """
        user_input = self.query_one("#input_chat", Input).value
        self.query_one("#chat_scroll", VerticalScroll).mount(
            SystemUserResponse(user_input)
        )
        self.query_one("#input_chat", Input).clear()

        response = self.chatbot_agent.chat(user_input, False)

        self.query_one("#chat_scroll", VerticalScroll).mount(
            SystemFridaResponse(response)
        )

        code_blocks = self.frida_coder.prepare(response)

        if len(code_blocks) > 0:
            for i, code_block in enumerate(code_blocks):
                # Confirmation to run the code
                self.query_one("#chat_scroll", VerticalScroll).mount(
                    RunCodeConfirmation(
                        id=f"run_code_confirmation_{i}",
                        frida_coder=self.frida_coder,
                        code_block=code_block,
                        files_required=list(self.chatbot_agent.get_files_required()),
                        files_open=self.chatbot_agent.is_files_open(),
                    ),
                )
        self.query_one("#chat_scroll", VerticalScroll).scroll_down(animate=True)

    def _on_mount(self, event: Mount):
        pass

    def on_button_pressed(self, event):
        """Event when a button in clicked"""
        button_pressed = str(event.button.id)
        if "cv_hs_file_" in button_pressed:
            file_name = button_pressed.replace("cv_hs_file_", "")
            convert_file_name = file_name.replace("-", ".")
            logger.info(__name__, f"convert_file_name: {convert_file_name}")
            path = self.file_manager.get_file_path(convert_file_name)
            self.display_code_file(path)
