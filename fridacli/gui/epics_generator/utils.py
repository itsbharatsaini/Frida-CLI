import json
import datetime

from fridacli.chatbot import ChatbotAgent
from fridacli.logger import Logger
import re
import csv

chatbot_agent = ChatbotAgent()
logger = Logger()

def save_project(path, projects):
    try:
        json_string = json.dumps(projects)
        with open(path, "w") as f:
            f.write(json_string)
        return True
    except Exception as e:
        return False

def get_data_from_file(path):
    try:
        with open(path, "r")  as f:
            data = f.read()
        return json.loads(data)
    except Exception as e:
        return None

def save_csv(path, project):
    logger.info(__name__, "project in save csv:" + str(project))
    try:
        with open(path, "w") as file:
            writer = csv.DictWriter(file, fieldnames=['epic', 'user_story', 'description', 'acceptance_criteria', 'out_of_scope'])
            writer.writeheader()
            for epic in project["epics"]:
                for user_stories in epic["user_stories"]:
                    dictionary = {
                        'epic': epic["epic_name"],
                        'user_story': user_stories["user_story"],
                        'description': user_stories["description"],
                        'acceptance_criteria': user_stories["acceptance_criteria"],
                        'out_of_scope': user_stories["out_of_scope"]
                    }
                    writer.writerow(dictionary)
            return True
    except Exception as e:
        return False

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

def generate_project_with_csv(project_name, project_description, plataform, date, csv_data):

    epics = []
    for key in csv_data.keys():
        epic = {
          "epic_name": key,
          "user_stories": csv_data[key]
        }
        epics.append(epic)

    project = {
      "project_name": project_name,
      "project_description": project_description,
      "plataform": plataform,
      "date": str(date),
      "versions": [
        {
          "version_name": "v1",
          "epics": epics
        }
      ]
    }

    return project

def get_code_block(text):
    try:
        code_pattern = re.compile(r"```([\w#]*)\n(.*?)```", re.DOTALL)
        matches = code_pattern.findall(text)
        code_blocks = [
            {
                "language": match[0],
                "code": match[1],
            }
            for match in matches
        ]
        if code_blocks == []:
            logger.info(__name__, f"Revisar: {text}")
        return code_blocks
    except Exception as e:
        pass

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

def complete_epic(epic, description):
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
    and the project description:
    {description}
    Complete the missing values respresenting with empty spaces, using the same structure
    NOT FORGET TO complete all
    IMPORTANT Responde ONLY with the json text updated with all the fields filled:
    """
    trys = 4
    # Try 3 times until the response is the expected
    for i in range(trys):
        response = chatbot_agent.chat(prompt, True)
        logger.info(__name__, response)
        try:
            json_response = json.loads(response)
            if has_expected_epic_structure(expected_structure, json_response):
                logger.info(__name__, str(json_response))
                return json_response
            else:
                logger.info(__name__, "not the same")
                return None
        except Exception as e:
            blocks = get_code_block(response)
            if len(blocks) > 0:
                json_response = blocks[0]["code"]
                json_response = json.loads(json_response)
                logger.info(__name__, "blocks " + str(json_response))
                if has_expected_epic_structure(expected_structure, json_response):
                    return json_response
    return None


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
