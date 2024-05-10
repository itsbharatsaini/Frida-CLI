from textual.screen import Screen
from textual.widgets import Static


class Project(Static):
    def compose(self):
        yield Label("hello")
