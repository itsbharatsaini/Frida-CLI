from .chat_responses.system_response import SystemUserResponse, SystemFridaResponse
from textual.containers import VerticalScroll, Vertical, HorizontalScroll, Horizontal
from .chat_responses.code_change_question import RunCodeConfirmation
from textual.widgets import Static, Input, Button, LoadingIndicator
from textual.worker import Worker, WorkerState
from fridacli.file_manager import FileManager
from fridacli.frida_coder import FridaCoder
from fridacli.chatbot import ChatbotAgent
from textual.app import ComposeResult
from rich.traceback import Traceback
from fridacli.logger import Logger
from textual.events import Mount
from rich.syntax import Syntax
from fridacli.config import OS
from .code_view import CodeView

logger = Logger()


class ChatView(Static):
    chatbot_agent = ChatbotAgent()
    frida_coder = FridaCoder()
    file_manager = FileManager()
    mentioned_files = []
    file_open = ""
    chat_label_sz = 0
    chat_response = ""
    run_code_confirmation_counter = 0

    CSS_PATH = "tcss/frida_styles.tcss"

    def compose(self) -> ComposeResult:
        logger.info(__name__, "Composing ChatView")

        with Vertical(classes="chat_view_vertical"):
            with VerticalScroll(id="chat_scroll"):
                yield SystemFridaResponse(
                    "Hey there! Welcome to Frida, your go-to code buddy. Let's make coding awesome together!"
                )
            yield Input(id="input_chat")
            yield HorizontalScroll(id="cv_hs")

    def mount_file_button(self, path, in_chat):
        """
            Mount children in the HorizontalScroll representing the files opened
        """
        logger.info(__name__, f"(mount_file_button) Mounting file button from path: {path} and in_chat: {in_chat}")
        file_name = path.split("\\")[-1] if OS == "win" else path.split("/")[-1]
        logger.info(__name__, f"(mount_file_button) mentioned_files: {self.mentioned_files} and file_open: {self.file_open}")
        if file_name not in self.mentioned_files and self.file_open != file_name:
            if in_chat:
                self.mentioned_files.append(file_name)
            else:
                self.file_open = file_name

            id = file_name.replace(".", "---")
            self.query_one("#cv_hs", HorizontalScroll).mount(
                Button(
                    str(file_name),
                    id=f"cv_hs_file_{id}",
                    classes="cv_hs_file_label",
                )
            )

    def delete_file_button(self, file_name, in_chat):
        """
        Delete children in the HorizontalScroll representing the files
        mentioned in the Input
        """
        logger.info(__name__, f"(delete_file_button) Deleting file button with file name: {file_name} and in_chat: {in_chat}")
        id = file_name.replace(".", "---")

        try:
            if in_chat:
                self.mentioned_files.remove(file_name)
            else:
                self.file_open = ""

            self.query_one("#cv_hs", HorizontalScroll).remove_children(
                f"#cv_hs_file_{id}"
            )
        except Exception as e:
            logger.error(__name__, f"(delete_file_button) Error deleting file button: {str(e)}")

    def display_code_file(self, path):
        """Change and display the file that was mentioned
        """
        logger.info(__name__, f"(display_code_file) Displaying code file from path: {path}")
        try:
            self.parent.parent.query_one(CodeView).update_file_code_view(path, True)
        except Exception as e:
            logger.error(__name__, f"(display_code_file) Error displaying code file: {str(e)}")
    
    async def chat_callback(self, user_input):
        """Callback function to chat with the chatbot"""
        logger.info(__name__, f"(chat_callback) Chat callback with user input: {user_input}")
        self.chatbot_agent.add_files_required(self.mentioned_files, self.file_open)
        self.chat_response = self.chatbot_agent.chat(user_input, False)

    def build_chatbot_response(self):
        """Build the chatbot response displaying on the chat"""
        logger.info(__name__, "(build_chatbot_response) Building chatbot response")
        loading_indicator = self.query_one("#loading_indicator", LoadingIndicator)
        if loading_indicator:
            loading_indicator.remove()

        chat_scroll = self.query_one("#chat_scroll", VerticalScroll)
        chat_scroll.mount(SystemFridaResponse(self.chat_response))

        code_blocks = self.frida_coder.prepare(self.chat_response)

        if len(code_blocks) > 0:
            for code_block in code_blocks:
                self.run_code_confirmation_counter += 1
                # Confirmation to run the code
                self.query_one("#chat_scroll", VerticalScroll).mount(
                    RunCodeConfirmation(
                        id=f"run_code_confirmation_{self.run_code_confirmation_counter}",
                        frida_coder=self.frida_coder,
                        code_block=code_block,
                        files_required=list(self.chatbot_agent.get_files_required()),
                        files_open=self.chatbot_agent.is_files_open(),
                    ),
                )
        self.query_one("#chat_scroll", VerticalScroll).scroll_down(animate=True)

    """Event handlers"""

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""

        logger.info(__name__, f"(on_input_changed) Input changed with message: {message.value}")
        text = message.value
        self.chat_label_sz = len(text)

        if len(self.mentioned_files) > 0:
            for file in self.mentioned_files:
                if file not in str(text):
                    self.delete_file_button(file, True)

        self.chat_label_sz = len(message.value)
        paths = self.chatbot_agent.get_matching_files(
            message.value, self.mentioned_files
        )
        if len(paths) > 0:
            for path in paths:
                self.mount_file_button(path, True)
                self.display_code_file(path)

    async def on_input_submitted(self):
        """Start the chat process """

        logger.info(__name__, "(on_input_submitted) Input submitted")
        user_input = str(self.query_one("#input_chat", Input).value)
        logger.info(__name__, f"(on_input_submitted) User input: {user_input}")
        self.query_one("#chat_scroll", VerticalScroll).mount(
            SystemUserResponse(user_input)
        )
        self.query_one("#input_chat", Input).clear()

        self.query_one("#chat_scroll", VerticalScroll).mount(
            LoadingIndicator(id="loading_indicator")
        )
        logger.info(__name__, f"(on_input_submitted) Running worker with user input")
        self.run_worker(self.chat_callback(user_input),  exclusive=False, thread=True)

    def on_button_pressed(self, event):
        """Event when a button in clicked"""
        logger.info(__name__, f"(on_button_pressed) Button pressed with event: {event.button.id}")
        button_pressed = str(event.button.id)
        if "cv_hs_file_" in button_pressed:
            file_name = button_pressed.split("_")[-1].replace("---", ".")
            path = self.file_manager.get_file_path(file_name)
            self.display_code_file(path)
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        logger.info(__name__, f"(on_worker_state_changed) Worker state changed with event: {str(event)}")
        if WorkerState.SUCCESS == event.worker.state and event.worker.name == "chat_callback":
            self.build_chatbot_response()
        logger.info(__name__, f"{event}")

    
