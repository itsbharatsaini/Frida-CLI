# TODO get the prompts from firebase
# TODO Make a list of special documentation types for each coding language

programming_languages = {
    ".cs": [
        "C#",
        """
    /// <summary>
    /// Summary text.
    /// </summary>
    /// <param name="param_name"></param>
    /// <returns>return type</returns>""",
    ]
}

def generate_document_prompt(code, extension):
    return f"""
    You are a professional coding and documentation assistant.
    You will be given a function written in {programming_languages[extension][0]}, and your job is to generate the appropriate documentation for it.

    Create a comprehensive documentation for the function given.
    Do NOT generate anything else besides the documentation.

    ALWAYS use this documentation style: {programming_languages[extension][1]}

    Your documentation should include a brief overview of the following:
    - Purpose of the function
    - Descriptions of input parameters
    - Return values
    - Exceptions handled in the function

    You have to return a code block with the function and the documentation.

    Do NOT alter the functions or omit them; only add the documentation.

    Do NOT add anything to the code block besides the documentation and the function.

    Do NOT write observations.

    ONLY respond with a code block, omit anything else.

    This is the function to document:
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
