from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Label, Button, MarkdownViewer
from .custom_labels import ResultErrorExceptionMessage
from fridacli.frida_coder.exception_message import ExceptionMessage
from fridacli.logger import Logger
import pyperclip

logger = Logger()

class RunCodeConfirmation(Static):

    def __init__(self, id, frida_coder, code_block, files_required, files_open) -> None:
        super().__init__(id=id)
        self.frida_coder = frida_coder
        self.code_block = code_block
        self.files_required = files_required
        self.files_open = files_open
        logger.info(__name__, f"""RunCodeConfirmation
            files_required: {str(self.files_required)}
            files_open: {str(self.files_open)}
        """)

    def compose(self):
        logger.info(__name__, "Composing RunCodeConfirmation")
        with Vertical(id="rcc_vertical"):
            yield Label("Do you want me to run the code?")
            with Horizontal(id="rcc_horizontal"):
                yield Button.success("Yes", id="btn_rcc_yes", classes="btn_rcc")
                yield Button.error("No", id="btn_rcc_no", classes="btn_rcc")

    def on_button_pressed(self, event):
        button_pressed = str(event.button.id)
        logger.info(__name__, f"(on_button_pressed) Button pressed: {button_pressed}")
        if button_pressed == "btn_rcc_yes":
            try:
                code_result = self.frida_coder.run(self.code_block, self.files_required)
                logger.info(__name__, f"(on_button_pressed) Code result: {str(code_result)}")
                if code_result["status"] == ExceptionMessage.RESULT_ERROR:
                    self.parent.parent.query_one("#chat_scroll", VerticalScroll).mount(
                        ResultErrorExceptionMessage()
                    )
                    self.parent.parent.query_one("#chat_scroll", VerticalScroll).mount(
                        MarkdownViewer(code_result["result"], classes="markdown_response")
                    )
                if code_result["status"] == ExceptionMessage.GET_RESULT_SUCCESS:
                    self.parent.parent.query_one("#chat_scroll", VerticalScroll).mount(
                        MarkdownViewer(
                            code_result["result"],
                            classes="markdown_response",
                            show_table_of_contents=False,
                        )
                    )
            except Exception as e:
                logger.error(__name__, f"(on_button_pressed) Error running code: {e}")
                self.app.notify(
                    "An error occurred running the code, check Python environment.", 
                    severity="error"
                )

        self.parent.parent.query_one("#chat_scroll", VerticalScroll).mount(
            CodeChangeQuestion(
                id = "code_change_question" + str(self.id),
                code=self.code_block["code"],
                frida_coder=self.frida_coder,
                files=self.files_required,
            )
        )
        self.remove()


class CodeChangeQuestion(Static):
    def __init__(self, id, code, frida_coder, files) -> None:
        super().__init__(id=id)
        self.code = code
        self.files = files
        self.frida_coder = frida_coder

        logger.info(__name__, f"""CodeChangeQuestion
            code: {str(self.code)}
            files: {str(self.files)}
        """)

    def compose(self):
        logger.info(__name__, f"Composing CodeChangeQuestion with files: {len(self.files)}")
        with Horizontal(id="ccq_horizontal"):
            if len(self.files) > 0:
                yield Button(
                    "Copy code", id="btn_copy_code", classes="btn_code_options"
                )
                yield Button(
                    "Apply changes",
                    id="btn_overwrite",
                    classes="btn_code_options",
                    variant="primary",
                )
                """
                TODO: Implement the commit creation
                yield Button(
                    "Create commit", id="btn_create_commit", classes="btn_code_options"
                )
                """
            else:
                yield Button(
                    "Copy code", id="btn_copy_code", classes="btn_code_options_nfr"
                )

    def on_button_pressed(self, event):
        button_pressed = str(event.button.id)
        logger.info(__name__, f"(on_button_pressed) Button pressed: {button_pressed}")
        if button_pressed == "btn_copy_code":
            pyperclip.copy(self.code)
            # TODO move all the str into a file to update from there
            self.notify("The code has been copied to the clipboard.")
        elif button_pressed == "btn_overwrite":
            if len(self.files) == 1:
                try:
                    path = self.frida_coder.get_file_manager().get_file_path(self.files[0])
                    logger.info(__name__, f"Overwriting file {path}")
                    self.frida_coder.write_code_to_path(path, self.code)
                    self.parent.parent.parent.parent.query_one("#code_view_pather").update_file_code_view(path, True)
                    self.notify("The file has been overwritten.")
                except Exception as e:
                    logger.error(__name__, f"(on_button_pressed) Error overwriting file: {e}")
                    self.notify("An error has occurred overwriting the file.")
        elif button_pressed == "btn_create_commit":
            pass
        self.remove()
