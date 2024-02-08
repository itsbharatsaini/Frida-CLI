from fridacli.interface.styles import add_styletags_to_string

def execution_result(result):
    return f"""The result of running the code for `{result['description']}` is: 
```
{result['result']}
```
"""

def error_chat_prompt(code, error):
    return f"""The code:
{code}
return me the follow error:
{error}
could you help me fix it.
"""

ERROR_CONFIRMATION_MESSAGE = "The generated code has errors, you want to ask for solutions?"
LANG_NOT_FOUND = "I apologize, but the current programming language used in the code is beyond my current proficiency, making it challenging for me to execute it at this moment."
RUN_CONFIRMATION_MESSAGE = "Shall I execute the generated code for you?"
WRITE_CONFIRMATION_MESSAGE = "You want to overwrite the content of the file?"