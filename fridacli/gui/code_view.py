from textual.containers import VerticalScroll, Vertical, Horizontal
from textual.widgets import DirectoryTree, Static, Select, Button
from fridacli.config import get_vars_as_dict
from rich.traceback import Traceback
from fridacli.logger import Logger
from textual.reactive import var
from rich.syntax import Syntax
from typing import Iterable
from pathlib import Path
from .push_screens import (
    EpicGenerator,
    DocGenerator,
    DocumentResultResume,
    MigrationDocGenerator,
)
from fridacli.config import OS
import subprocess
import os

logger = Logger()

LINES = ["Generate Documentation", "Migration"]


class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """
        Filter out paths that start with a dot or tilde.
        """
        logger.info(__name__, "(filter_paths) Filtering paths")
        return [path for path in paths if not path.name.startswith((".", "~"))]


class CodeView(Static):
    show_tree = var(True)
    CSS_PATH = "fridacli/gui/tcss/frida_styles.tcss"
    recipe_selected = ""
    file_button_open = ""

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self):
        logger.info(__name__, "(compose) Composing CodeView")
        path = get_vars_as_dict()["PROJECT_PATH"]
        logger.info(__name__, f"(compose) Project path: {path}")

        with Horizontal():
            with Vertical(id="code_view_left"):
                with Horizontal(id="code_view_buttons"):
                    yield Select((line, line) for line in LINES)
                    yield Button("Execute", id="btn_recipe")
                yield FilteredDirectoryTree(os.path.abspath(path), id="cv_tree_view")
            with VerticalScroll(id="cv_code_scroll"):
                yield Static(id="cv_code", expand=False)

    def on_mount(self) -> None:
        logger.info(__name__, "(on_mount) Mounting CodeView")
        self.query_one(DirectoryTree).focus()

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        """Called when the user click a file in the directory tree."""

        logger.info(
            __name__,
            f"(on_directory_tree_file_selected) File selected: {str(event.path)}",
        )
        event.stop()
        try:
            extension = event.path.suffix

            if extension == ".docx":
                if OS == "win":
                    os.startfile(event.path)
                else:
                    subprocess.call(("open", event.path))
            else:
                self.update_file_code_view(event.path, False)
        except Exception as e:
            logger.error(__name__, f"Error opening file: {e}")

    def update_file_code_view(self, path, is_chat):
        logger.info(__name__, f"update_file_code_view")
        code_view = self.query_one("#cv_code", Static)
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

            # If wasn't called from chat, update the file button
            if not is_chat:
                if self.file_button_open == "":
                    self.file_button_open = str(path)
                    self.parent.parent.query_one("#chat_view").mount_file_button(
                        str(path), False
                    )
                else:
                    file_name = (
                        self.file_button_open.split("\\")[-1]
                        if OS == "win"
                        else self.file_button_open.split("/")[-1]
                    )
                    self.parent.parent.query_one("#chat_view").delete_file_button(
                        file_name, False
                    )
                    self.file_button_open = str(path)
                    self.parent.parent.query_one("#chat_view").mount_file_button(
                        str(path), False
                    )

            self.query_one("#cv_code_scroll").scroll_home(animate=False)
            self.sub_title = str(path)

    def action_toggle_files(self) -> None:
        """Called in response to key binding."""
        self.show_tree = not self.show_tree

    def on_select_changed(self, event: Select.Changed) -> None:
        self.recipe_selected = str(event.value)

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        if button_pressed == "btn_recipe":
            if self.recipe_selected == "Generate Documentation":
                logger.info(__name__, "On UI calling to document files")
                self.app.push_screen(DocGenerator(), self.doc_generator_callback)

            elif self.recipe_selected == "Migration":
                self.app.push_screen(MigrationDocGenerator(), self.migration_generator_callback)

    def doc_generator_callback(self, result):
        self.app.push_screen(DocumentResultResume(result))
        self.query_one("#cv_tree_view", FilteredDirectoryTree).reload()


    def migration_generator_callback(self, result):
        self.query_one("#cv_tree_view", FilteredDirectoryTree).reload()