from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Static, Label, Button, MarkdownViewer
from .custom_labels import ResultErrorExceptionMessage
from fridacli.frida_coder.exception_message import ExceptionMessage
import pyperclip


class RunCodeConfirmation(Static):

    def __init__(self, id, frida_coder, code_block, files_required, files_open) -> None:
        super().__init__(id=id)
        self.frida_coder = frida_coder
        self.code_block = code_block
        self.files_required = files_required
        self.files_open = files_open

    def compose(self):
        with Vertical(id="rcc_vertical"):
            yield Label("Do you want me to run the code?")
            with Horizontal(id="rcc_horizontal"):
                yield Button.success("Yes", id="btn_rcc_yes", classes="btn_rcc")
                yield Button.error("No", id="btn_rcc_no", classes="btn_rcc")

    def on_button_pressed(self, event):
        button_pressed = str(event.button.id)
        if button_pressed == "btn_rcc_yes":
            code_result = self.frida_coder.run(self.code_block, self.files_required)
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

                self.parent.parent.query_one("#chat_scroll", VerticalScroll).mount(
                    CodeChangeQuestion(
                        id="code_change_question",
                        code=self.code_block["code"],
                        files_open=self.files_open,
                    )
                )
        self.remove()


class CodeChangeQuestion(Static):
    def __init__(self, id, code, files_open=False) -> None:
        super().__init__(id=id)
        self.code = code
        self.files_open = files_open

    def compose(self):
        with Horizontal(id="ccq_horizontal"):
            if self.files_open:
                yield Button(
                    "Copy code", id="btn_copy_code", classes="btn_code_options"
                )
                yield Button(
                    "Overwrite", id="btn_overwrite", classes="btn_code_options"
                )
                yield Button(
                    "Create commit", id="btn_create_commit", classes="btn_code_options"
                )
            else:
                yield Button(
                    "Copy code", id="btn_copy_code", classes="btn_code_options_nfr"
                )

    def on_button_pressed(self, event):
        button_pressed = str(event.button.id)
        if button_pressed == "btn_copy_code":
            pyperclip.copy(self.code)
            # TODO move all the str into a file to update from there
            self.notify("The code has been copied to the clipboard.")
        elif button_pressed == "btn_overwrite":
            pass
        elif button_pressed == "btn_create_commit":
            pass
        self.remove()
