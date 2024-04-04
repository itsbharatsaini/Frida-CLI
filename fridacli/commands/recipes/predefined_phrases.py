#TODO get the prompts from firebase

generate_document_prompt = lambda code: f"""
"You are a professional coding and documentation assistant.
Make sure to understand what coding language is being used in each file, they can vary within files and folders.
You will be given a file written in any coding language, and your job is to generate and add appropriate documentation for every function and class within the file.

Create a comprehensive documentation for the code given in a new code block.
Use the style conventions of the detected language for the documentation.

Your documentation should include a brief overview of the following:
- Purpose of the file
- Explanations of any functions or classes defined within the file
- Descriptions of input parameters
- Return values
- Any exceptions raised

Ensure that the documentation is either provided as docstrings within the code or as comments adjacent to functions and classes, according to the conventions of the detected coding language.

Do NOT alter the functions or omit them; only add the documentation.

Do NOT forget to include the rest of the code, not only the functions, classes and everything documented

This is the code to document:
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