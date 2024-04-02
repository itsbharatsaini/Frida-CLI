import csv
from .predefined_phrases import generate_epic
from fridacli.logger import Logger

logger = Logger()


def exec_generate_epics(chatbot_agent, text, path):
    epics = text.split(",")
    with open(f"{path}/output.csv", 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['epic', 'user_story', 'description', 'acceptance_criteria', 'out_of_scope'])
        writer.writeheader()
        for epic in epics:
            message = generate_epic(epic.strip())
            response = chatbot_agent.chat(message, True)
            logger.info(__name__, response)
            sections = response.strip().split("***")
            for section in sections:
                values = section.split("$$")
                if len(values) == 4:
                    user_story = values[0].split(":")[1] if ":" in values[0] else values[0]
                    description = values[1].split(":")[1] if ":" in values[1] else values[1]
                    acceptence_criteria = values[2].split(":")[1] if ":" in values[2] else values[2]
                    out_of_scope = values[3].split(":")[1] if ":" in values[3] else values[3]
                    dictionary = {
                        'epic': epic, 
                        'user_story': user_story, 
                        'description': description,
                        'acceptance_criteria': acceptence_criteria.lstrip('\n'),
                        'out_of_scope': out_of_scope
                        }
                    writer.writerow(dictionary)