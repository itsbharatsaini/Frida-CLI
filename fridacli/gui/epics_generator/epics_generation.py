from logging import disable
from typing_extensions import Text
from textual.containers import  VerticalScroll, Vertical, Horizontal, Center, Grid
from textual.widgets import Static, Select, Button, Label, Rule, Input, ListView, ListItem
from fridacli.gui.push_screens import CreateNewEpic
from fridacli.logger import Logger
from .utils import get_data_from_file, get_project_versions, get_versions_name
from datetime import datetime

logger = Logger()

LINES = """Version 1
Version 2
Version 3
""".splitlines()

class ListProjectItem(Static):
    def __init__(self, project) -> None:
        super().__init__()
        self.project = project

    def compose(self):
        with Grid(id = "list_project_item"):
            yield Label("Project name: " + self.project["project_name"], classes = "list_project_label")
            yield Label("Last updated: " + self.project["date"], classes = "list_project_label")
            yield Label("Plataform: " + self.project["plataform"])

class EpicsGeneration(Static):
    PATH = "data.json"
    #Contains all of the version
    versions = {}
    validation = False
    def __init__(self) -> None:
        super().__init__()
        #self.compose()
        #self.load_projects()

    def compose(self):
        with Horizontal(id="a"):
            with Vertical(id="epics_side_bar"):
                yield Label("Projects")
                yield Button("New Project")
            with Vertical(id="epics_content"):
                with Horizontal(classes = "epics_header_cls"):
                    yield Input(id="epics_search_input", placeholder="Search project")
                    yield Button("Search", id="epics_search_btn")
                    yield Button("New Project", id="create_new_project_btn", variant="success")
                yield Rule()
                with Horizontal(classes = "epics_header_cls"):
                    #This part should be changed depending on the situation
                    with Horizontal(id="epics_container_select"):
                        yield Select(options = [(line, line) for line in LINES], prompt="Version", id="epics_select", disabled=True)
                        if self.validation:
                            yield Button("Edit", disabled=True)
                            yield Button("Download", disabled=True)
                with VerticalScroll(id="project_content"):
                    yield ListView(id="list_view_container")

    def on_mount(self):
        self.load_projects()

    def load_projects(self):
        #Get the raw data from file
        data = get_data_from_file(self.PATH)
        logger.info(__name__, str(data))

        if data != None:
            if data.get("projects") != -1:
                #Trasnform the data
                projects = data["projects"]

                #Get the list view
                list_view = self.query_one("#list_view_container", ListView)
                list_view.clear()

                #Populate all the projects stored
                if len(projects) > 0:
                    for project in data["projects"]:
                        list_view.append(ListItem(ListProjectItem(project)))
                        versions_name = get_versions_name(project)

                        #Update the select options
                        self.update_select_options(versions_name)
            else:
                self.notify("No projects found", severity="error")
        else:
            pass
            #self.notify("No file found", severity="error")

    def update_select_options(self, options):
        select = self.query_one("#epics_select", Select)
        new_options = [(line, line) for line in options]
        select.set_options(new_options)

    def create_new_project_callback(self, params):
        # project_name, plataform, project_description
        epic_name, plataform, project_context = params
        date = datetime.now()
        formatted_time = date.strftime('%Y-%m-%d %H:%M:%S')
        logger.info(__name__, params)
        list_view = self.query_one("#list_view_container", ListView)
        #Create new ListProjectItem
        list_view.append(ListItem(ListProjectItem(epic_name, formatted_time, project_context)))

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        if button_pressed == "create_new_project_btn":
            self.app.push_screen(CreateNewEpic(), self.create_new_project_callback)
        elif button_pressed == "epics_search_btn":
            logger.info(__name__, "helllo")

    def on_list_view_selected(self, event: ListView.Selected):
        selected = event.item.query_one(ListProjectItem)
        content = self.query_one("#project_content", VerticalScroll)
        #Delete the projects list since a proyect has been selected
        content.remove_children("#list_view_container")
        content.mount(Project())
