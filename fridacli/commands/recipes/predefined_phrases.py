# TODO get the prompts from firebase


# The dictionary is structured as follows:
# extension : [name, example of function documentation]
programming_languages = {
    ".cs": [
        "C#",
        """
    /// <summary>
    /// Purpose of the funtion.
    /// Detailed description of the function.
    /// </summary>
    /// <param name="param_name">Description of the parameter.</param>
    /// <returns>Description of the return value.</returns>
    /// <exception cref="exception_name">Description of the exception.</exception>""",
    ],
    ".py": [
        "Python",
        '''
    """
    Detailed description of the function and it\'s purpose.

    Args:
        param_name (param_type): Description of the parameter.

    Returns:
        return_type: Description of the return value.

    Raises:
        Exception_name: Description of the exception.
    """''',
    ],
    ".java": [
        "Java",
        """
    /**
     * Detailed description of the function and it's purpose.
     *
     * @param paramName description of the parameter.
     * @return description of the return value.
     * @throws ExceptionName description of the exception.
     */""",
    ],
    ".js": [
        "Javascript",
        """
    /**
    * Calculates the square root of a number.
    *
    * @param {param_type} paramName - Description of the parameter.
    * @returns {return_type} Description of the return value.
    * @throws {ErrorName} Description of the exception.
    */""",
    ],
}


# Used to generate documentation for a full code file
def generate_full_document_prompt(code, extension):
    return f"""
    You are a professional coding and documentation assitant.
    You will be given a code written in {programming_languages[extension][0]} and your job is to generate and add the appropiate documentation for it.
    
    Create a comprehensive documentation for each function.
    You MUST responde with a code block that contains both the generated documentation and the given code.
    
    Each function must be documented with:
    - Purpose of the function with a detailed description of what the function does.
    - Descriptions of input parameters if any.
    - Return values if any.
    - Exceptions handled in the function if any.

    ALWAYS use this documentation style for the functions: {programming_languages[extension][1]}

    DO NOT OMIT ANYTHING.

    DO NOT OMIT ANY FUNCTION.
    
    DO NOT OMIT THE BODY OF ANY FUNCTION.

    RETURN ONLY ONE CODE BLOCK.

    Do NOT document classes.

    Do NOT add 'Example usage' in the documentation of the function.

    Do NOT generate anything else besides the documentation.

    Do NOT alter the code or omit them; only add the documentation.

    Do NOT add anything to the code block besides the documentation and the code.

    Do NOT write observations.

    ONLY respond with a code block, omit anything else.

    This is the code to document:
    {code}
    """


# Generates documentation for only one function
def generate_document_for_funct_prompt(code, extension):
    return f"""
    You are a professional coding and documentation assistant.
    You will be given a function written in {programming_languages[extension][0]}, and your job is to generate the appropriate documentation for it.

    Create a comprehensive documentation for the function given.
    Do NOT generate anything else besides the documentation.

    ALWAYS use this documentation style: {programming_languages[extension][1]}

    Your documentation should include a brief overview of the following:
    - Purpose of the function with a detailed description of what the function does.
    - Descriptions of input parameters
    - Return values
    - Exceptions handled in the function

    The description of the function MUST be within the code block.

    The description of the function MUST be written with natural language.

    You have to return a code block with the function and the documentation.

    Always follow the best documentation practices.

    Do NOT omit the function.

    RETURN ONLY ONE CODE BLOCK.

    Do NOT alter the function; only add the documentation.

    Do NOT add anything to the code block besides the documentation and the function.

    Do NOT write observations.

    ONLY respond with a code block, omit anything else.

    This is the function to document:
    {code}
    """


generate_epic = (
    lambda epic_name: f"""Generate at least 5 user stories for the Epic {epic_name} in the project Innovasports Mobile, which is a mobile application designed for selling shoes.
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
)
