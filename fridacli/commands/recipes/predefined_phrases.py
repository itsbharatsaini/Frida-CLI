#TODO get the prompts from firebase

generate_document_prompt = lambda code: f"""
"Create a comprehensive documentation for the code given in a new block code.
For that use the stadards, example if the code is in python use Pep8 
Your documentation should include a brief overview of the purpose of the file, 
explanations of any functions or classes defined within the file, descriptions of input parameters, 
return values, and any exceptions raised.
Do not forget to create the block code with the code documentated
The code to document is the follow:
{code}
"""

generate_epic = lambda epic_name: f"""Generate at least 5 user stories for the Epic {epic_name} in the project Innovasports Mobile, which is a mobile application designed for selling shoes.
Each user story should consist of a title, a detailed description, and acceptance criteria to ensure clarity and understanding.

Use the following format for each user story:
***
Title: [Title of the user story]
$$
Description: [Detailed description of the user story, including the specific action or functionality it describes]
$$
Acceptance Criteria:
- [Condition 1 that must be met for the user story to be considered complete]
- [Condition 2 that must be met for the user story to be considered complete]
- [Condition 3 that must be met for the user story to be considered complete]
$$
Out of scope:
- [Aspect 1 that is out of scope]
- [Aspect 2 that is out of scope]
- [Aspect 3 that is out of scope]
***
Use '***' to separate every user story
"""