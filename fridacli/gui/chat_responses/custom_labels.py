from textual.widgets import Static, Label

class ResultErrorExceptionMessage(Static):
    def compose(self):
        yield Label("An error has been identified within the code.", classes="reem_label")

