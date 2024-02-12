from yaspin import yaspin
from yaspin.spinners import Spinners
from yaspin.core import Spinner


class Spinner:
    def __init__(self) -> None:
        self.system_spinner = yaspin()

    def start_spinner(self, spinner: Spinner = Spinners.point, text: str = "") -> None:
        self.system_spinner.spinner = spinner
        self.system_spinner.text = text
        self.system_spinner.start()

    def stop_spinner(self) -> None:
        self.system_spinner.stop()
