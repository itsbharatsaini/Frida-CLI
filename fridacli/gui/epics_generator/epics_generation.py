from logging import disable
from typing_extensions import Text
from textual.containers import  VerticalScroll, Vertical, Horizontal, Center, Grid, Middle
from textual.widgets import Static, Select, Button, Label, Rule, Input, ListView, ListItem
from fridacli.gui.push_screens import CreateNewEpic
from fridacli.logger import Logger
from .utils import get_data_from_file, get_project_versions, generate_empty_project, save_project
from datetime import datetime
from .project import Project


logger = Logger()

class ListProjectItem(Static):
    def __init__(self, project, idx) -> None:
        super().__init__()
        self.project = project
        #Index of the project in Data
        self.idx = idx

    def compose(self):
        with Grid(id = "list_project_item"):
            yield Label("Project name: " + self.project["project_name"], classes = "list_project_label")
            yield Label("Last updated: " + self.project["date"], classes = "list_project_label")
            yield Label("Plataform: " + self.project["plataform"])

class EpicsGeneration(Static):
    PATH = "data.json"
    AUX_PATH = "data2.json"
    #Contains all of the version
    versions = {}
    validation = False
    project_size = 0
    selected_project = ""
    projects = {}

    def __init__(self) -> None:
        super().__init__()

    def compose(self):
        with Horizontal(id="a"):
            with Vertical(id="epics_side_bar"):
                yield Label("Projects")
                yield Button("New Project")
            with Vertical(id="epics_content"):
                with Horizontal(classes = "epics_header_cls"):
                    yield Input(id="epics_search_input", placeholder="Search project")
                    yield Button("Search", id="epics_search_btn", variant="primary")
                    yield Button("New Project", id="create_new_project_btn", variant="success")
                yield Rule()
                with VerticalScroll(id="project_content"):
                    yield ListView(id="list_view_container")

    def on_mount(self):
        self.load_projects()

    def load_projects(self):
        #Get the raw data from file
        data = get_data_from_file(self.AUX_PATH)
        self.projects = data
        logger.info(__name__, str(data))

        if data != None:
            if data.get("projects") != -1:
                #Trasnform the data
                projects = data["projects"]
                self.project_size = len(projects)

                #Get the list view
                list_view = self.query_one("#list_view_container", ListView)
                list_view.clear()

                #Populate all the projects stored
                if len(projects) > 0:
                    for idx, project in enumerate(data["projects"]):
                        list_view.append(ListItem(ListProjectItem(project, idx)))
            else:
                self.notify("No projects found", severity="error")
        else:
            pass
            #self.notify("No file found", severity="error")

    def save_projects(self):
        logger.info(__name__, "saving projetcsssss")
        content = self.query_one("#project_content", VerticalScroll)
        project = content.query_one(Project)
        project_new_data = project.get_data()

        for project in self.projects["projects"]:
            if project["project_name"] == self.selected_project:
                project = project_new_data

        status = save_project(self.AUX_PATH, self.projects)

        if status:
            self.notify("The project was saved successfully")
        else:
            self.notify("An error occurred while saving the project.")



    def create_new_project_callback(self, params):
        # project_name, plataform, project_description
        project_name, plataform, project_description = params
        date = datetime.now()
        formatted_time = date.strftime('%Y-%m-%d %H:%M:%S')
        list_view = self.query_one("#list_view_container", ListView)
        #Create new ListProjectItem
        project = generate_empty_project(project_name, project_description, plataform, formatted_time)
        logger.info(__name__, "project" + str(project))
        list_view.append(ListItem(ListProjectItem(project, self.project_size + 1)))
        self.project_size += 1

    def on_button_pressed(self, event: Button.Pressed):
        button_pressed = str(event.button.id)
        if button_pressed == "create_new_project_btn":
            self.app.push_screen(CreateNewEpic(), self.create_new_project_callback)
        elif button_pressed == "epics_search_btn":
            logger.info(__name__, "helllo")

    def on_list_view_selected(self, event: ListView.Selected):
        selected = event.item.query_one(ListProjectItem)
        content = self.query_one("#project_content", VerticalScroll)
        self.selected_project = selected.project["project_name"]
        #Delete the projects list since a proyect has been selected
        content.remove_children("#list_view_container")
        content.mount(Project(self.PATH, selected.project, selected.idx, self.save_projects))
