import json
import datetime

from fridacli.chatbot import ChatbotAgent
from fridacli.logger import Logger

chatbot_agent = ChatbotAgent()
logger = Logger()

def save_project(path, project):
    with open(path, "w") as f:
        f.write(project)

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

def has_expected_epic_structure(expected_structure, json_obj):
    # Function to compare the structure of two JSON objects
    def compare_structure(json1, json2):
        if isinstance(json1, dict) and isinstance(json2, dict):
            if set(json1.keys()) != set(json2.keys()):
                return False
            for key in json1.keys():
                if not compare_structure(json1[key], json2[key]):
                    return False
            return True
        elif isinstance(json1, list) and isinstance(json2, list):
            if not json1 and not json2:
                return True  # Both lists are empty
            if not json1 or not json2:
                return False  # One list is empty and the other is not
            # Assuming all elements in the list should have the same structure
            for item in json2:
                if not compare_structure(json1[0], item):
                    return False
            return True
        else:
            return True  # For non-dict and non-list items, we assume the structure is valid

    # Call the compare structure function with the expected structure and the provided JSON object
    return compare_structure(expected_structure, json_obj)

def create_generated_epic(epic, name, empty):
    # Create a new generated Epic using IA or a empty Epic
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

    if empty:
        expected_structure["user_story"] = name
        return expected_structure

    prompt = f"""
    Given the following information:
    {epic}

    {
        "Create a new different Epic from the already given with this format"
        if len(name) == 0
        else "Create a new different Epic from the already named " + name + "given with this format"
    }
    IMPORTANT Responde ONLY with the json:
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
    # Try 3 times until the response is the expected
    for i in range(3):
        response = chatbot_agent.chat(prompt, True)
        try:
            json_response = json.loads(response)
            if has_expected_epic_structure(expected_structure, json_response):
                logger.info(__name__, str(json_response))
                return json_response
            else:
                logger.info(__name__, "not the same")
        except Exception as e:
            logger.info(__name__, "error")
    return expected_structure

def create_generated_user_story(user_story, name, empty):
    expected_structure = {
        "user_story": "",
        "description": "",
        "acceptance_criteria": "",
        "out_of_scope": ""
    }

    if empty:
        expected_structure["user_story"] = name
        return expected_structure

    prompt = f"""
    Given the following information:
    {user_story}

    {
        "Create a new different User Story from the already given with this format"
        if len(name) == 0
        else "Create a new different User Story from the already named " + name + "given with this format"
    }

    IMPORTANT Responde ONLY with the json:
    {{
        "user_story": "",
        "description": "",
        "acceptance_criteria": "",
        "out_of_scope": ""
    }}
    """
    trys = 3
    for i in range(3):
        response = chatbot_agent.chat(prompt, True)
        logger.info(__name__, "response" + str(response))

        try:
            json_response = json.loads(response)
            if has_expected_epic_structure(expected_structure, json_response):
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

def complete_epic(epic):
    # Create a new generated Epic using IA or a empty Epic
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

    prompt = f"""
    Given the following information:
    {epic}
    Complete the missing values respresenting with empty spaces, using the same structure
    NOT FORGET TO complete all
    IMPORTANT Responde ONLY with the json updated:
    """
    trys = 4
    # Try 3 times until the response is the expected
    for i in range(3):
        response = chatbot_agent.chat(prompt, True)
        logger.info(__name__, response)
        try:
            json_response = json.loads(response)
            if has_expected_epic_structure(expected_structure, json_response):
                logger.info(__name__, str(json_response))
                return json_response
            else:
                logger.info(__name__, "not the same")
        except Exception as e:
            logger.info(__name__, "error")
    return expected_structure


def create_empty_userstory():
    return {
      "user_story": "",
      "description": "",
      "acceptance_criteria": "",
      "out_of_scope": ""
    }

def create_empty_epic(name):
   return {
     "epic_name": name,
     "user_stories": [
       {
         "user_story": "",
         "description": "",
         "acceptance_criteria": "",
         "out_of_scope": ""
       }
     ]
   }
