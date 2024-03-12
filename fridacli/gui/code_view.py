from textual.containers import  VerticalScroll, Vertical, Horizontal
from textual.widgets import DirectoryTree, Static, Select, Button
from fridacli.config import get_vars_as_dict
from rich.traceback import Traceback
from textual.reactive import var
from rich.syntax import Syntax
from typing import Iterable
from pathlib import Path



LINES = """document
asp_voyager
""".splitlines()

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]
    
class CodeView(Static):
    show_tree = var(True)
    CSS_PATH = "tcss/frida_styles.tcss"

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self):
        path = get_vars_as_dict()["PROJECT_PATH"]
        with Horizontal():
            with Vertical(id="code_view_left"):
                with Horizontal(id="code_view_buttons"):
                    yield Select((line, line) for line in LINES)
                    yield Button("Execute")
                yield FilteredDirectoryTree(path, id="cv_tree_view")
                yield Button("Update directory", id="btn_code_view_update_directory")
            with VerticalScroll(id="cv_code_scroll"):
                yield Static(id="cv_code", expand=False)

    def on_mount(self) -> None:
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""
        event.stop()
        code_view = self.query_one("#cv_code", Static)
        
        try:
            syntax = Syntax.from_path(
                str(event.path),
                line_numbers=True,
                word_wrap=False,
                indent_guides=True,
                theme="github-dark",
                highlight_lines=[1, 2, 4, 6, 7],
            )
        except Exception:
            code_view.update(Traceback(theme="github-dark", width=None))
            self.sub_title = "ERROR"
        else:
            code_view.update(syntax)
            self.query_one("#cv_code_scroll").scroll_home(animate=False)
            self.sub_title = str(event.path)

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

    #def watch_path(self): to watch changes

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        if button_pressed == "btn_code_view_update_directory":
            tree_view = self.query_one("#cv_tree_view", FilteredDirectoryTree)
            tree_view.reload()
            self.notify(f"File directory updated {tree_view.root}")
