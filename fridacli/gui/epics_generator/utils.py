import json
import datetime

from fridacli.chatbot import ChatbotAgent
from fridacli.logger import Logger
import re
import csv

chatbot_agent = ChatbotAgent()
logger = Logger()

def save_project(path, projects):
    """Save the projects in a json file"""
    try:
        json_string = json.dumps(projects)
        with open(path, "w") as f:
            f.write(json_string)
        return True
    except Exception as e:
        return False

def get_data_from_file(path):
    """Get the data from a json file"""
    try:
        with open(path, "r")  as f:
            data = f.read()
        return json.loads(data)
    except Exception as e:
        return None

def save_csv(path, project):
    """Save the project in a csv file"""
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
    """Get the versions of a project"""

    for project in data["project"]:
        if project["project_name"] == project_name:
            return project

def get_versions_names(project):
    """Get the names of the versions of a project"""

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
    """Generate a project with the data from a csv file"""

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
    """Get the code blocks from a text"""

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
    """Check if the json object has the expected structure"""

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

async def create_generated_epic(epic, name, empty, project_description):
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
    and the project description:
    {project_description}

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
    logger.info(__name__, "Prompttt: " + prompt)
    trys = 3
    # Try 3 times until the response is the expected
    for i in range(trys):
        response = chatbot_agent.chat(prompt, True)
        try:
            json_response = json.loads(response)
            if has_expected_epic_structure(expected_structure, json_response):
                logger.info(__name__, str(json_response))
                return json_response
            else:
                logger.info(__name__, "not the same")
        except Exception as e:
            blocks = get_code_block(response)
            if len(blocks) > 0:
                json_response = blocks[0]["code"]
                json_response = json.loads(json_response)
                logger.info(__name__, "blocks " + str(json_response))
                if has_expected_epic_structure(expected_structure, json_response):
                    return json_response
    return {}

async def create_generated_user_story(user_story, name, empty, project_description):
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
    and the project description:
    {project_description}
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
    logger.info(__name__, "Prompttt: " + prompt)
    trys = 3
    for i in range(trys):
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
            blocks = get_code_block(response)
            if len(blocks) > 0:
                json_response = blocks[0]["code"]
                json_response = json.loads(json_response)
                logger.info(__name__, "blocks " + str(json_response))
                if has_expected_epic_structure(expected_structure, json_response):
                    return json_response
    return {}
async def complete_epic(epic, description):
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
    return {}

async def enhance_project_description(description):
    prompt = f"""
    Enhance the project description below by providing more detail without introducing any new elements:
    {description}
    IMPORTANT Response ONLY with the enhanced project description.
    """
    response = chatbot_agent.chat(prompt, True)
    return response

async def complete_epic_cell(user_story, id):
    text_type = ""  
    if id == "userstory_name":
        text_type = "user story name"
    elif id == "userstory_description":
        text_type = "user story description"
    elif id == "userstory_acceptance_criteria":
        text_type = "user story acceptance criteria"
    elif id == "userstory_out_of_scope":
        text_type = "user story out of scope"

    prompt = f"""
    Complete the {text_type} in the follow user story:
    {user_story}
    IMPORTANT Response ONLY with the {text_type}.
    """
    response = chatbot_agent.chat(prompt, True)
    return response

async def enhance_text(text, id):
    text_type = ""  
    if id == "userstory_name":
        text_type = "user story name"
    elif id == "userstory_description":
        text_type = "user story description"
    elif id == "userstory_acceptance_criteria":
        text_type = "user story acceptance criteria"
    elif id == "userstory_out_of_scope":
        text_type = "user story out of scope"

    prompt = f"""
    Enhance the {text_type} below by providing more detail without introducing any new elements:
    {text}
    IMPORTANT Response ONLY with the enhanced text.
    """
    response = chatbot_agent.chat(prompt, True)
    return response

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
