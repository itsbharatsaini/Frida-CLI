import json

def get_data_from_file(path):
    try:
        with open(path, "r")  as f:
            data = f.read()
        return json.loads(data)
    except Exception as e:
        return None

def get_project_versions(project_name, data):
    for project in data["project"]:
        if project["project_name"] == project_name:
            return project

def get_versions_name(project):
    versions = project["versions"]
    return [ version["version_name"] for version in versions]
