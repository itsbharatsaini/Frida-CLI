from textual.widgets import Static, Label, MarkdownViewer
from fridacli.config import get_username


class SystemUserResponse(Static):
    def compose(self):
        yield Label(f"[#00ebeb]{get_username()}>[/] {self.renderable}", classes="chat_label")

class SystemFridaResponse(Static):
    def compose(self):
        yield Label(f"[#A4CE95]frida>[/]", classes="chat_label")
        yield MarkdownViewer(str(self.renderable), classes = "chat_markdown", show_table_of_contents=False)
