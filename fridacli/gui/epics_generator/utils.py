import json
import datetime

from fridacli.chatbot import ChatbotAgent
from fridacli.logger import Logger

chatbot_agent = ChatbotAgent()
logger = Logger()

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

def get_versions_names(project):
    versions = project["versions"]
    return [ version["version_name"] for version in versions]

def generate_empty_project(project_name, project_description, plataform, date):
    project = {
      "project_name": project_name,
      "project_description": project_description,
      "plataform": plataform,
      "date": str(date),
      "versions": [
        {
          "version_name": "v1",
          "epics": [
            {
              "epic_name": "",
              "user_stories": [
                {
                  "user_story": "",
                  "description": "",
                  "acceptance_criteria": "",
                  "out_of_scope": ""
                }
              ]
            }
          ]
        }
      ]
    }
    return project

def has_expected_epic_structure(json_obj):
    expected_structure = {
        "epic_name": "",
        "user_stories": [
            {
                "user_story": "",
                "description": "",
                "acceptance_criteria": "",
                "out_of_scope": ""
            }
        ]
    }

    def compare_structure(json1, json2):
        if isinstance(json1, dict) and isinstance(json2, dict):
            if set(json1.keys()) != set(json2.keys()):
                return False
            for key in json1.keys():
                if not compare_structure(json1[key], json2[key]):
                    return False
            return True
        elif isinstance(json1, list) and isinstance(json2, list):
            if len(json1) != len(json2):
                return False
            for item1, item2 in zip(json1, json2):
                if not compare_structure(item1, item2):
                    return False
            return True
        else:
            return True

    return compare_structure(expected_structure, json_obj)

def create_new_epic(epic):
    prompt = f"""
    Given the following information:
    {epic}

    Create a new different Epic from the already given with this format IMPORTANT Responde ONLY with the json:
    {{
        "epic_name": "",
        "user_stories": [
        {{
            "user_story": "",
            "description": "",
            "acceptance_criteria": "",
            "out_of_scope": ""
        }}
        ]
    }}
    """
    trys = 3
    for i in range(3):
        response = chatbot_agent.chat(prompt, True)
        logger.info(__name__, "response" + str(response))
        try:
            json_response = json.loads(response)
            if has_expected_epic_structure(json_response):
                logger.info(__name__, str(json_response))
                return json_response
            else:
                logger.info(__name__, "not the same")
        except Exception as e:
            logger.info(__name__, "error")
    return {
            "user_story": "",
            "description": "",
            "acceptance_criteria": "",
            "out_of_scope": ""
        }


def create_empty_userstory():
    return {
      "user_story": "",
      "description": "",
      "acceptance_criteria": "",
      "out_of_scope": ""
    }
