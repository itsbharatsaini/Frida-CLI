from fridacli.interface.styles import add_styletags_to_string

ANGULAR_PROJECT_DETECTED = f"{add_styletags_to_string('- Angular project detected', style='success')} voyager started..."
ANGULAR_PROJECT_NOT_DETECTED = f"{add_styletags_to_string('- Angular project not detected', style='warning')}"
ANGULAR_PROJECT_NOT_DETECTED = (
    lambda path: f"{add_styletags_to_string('- Angular project not detected in',style='warning')} {add_styletags_to_string(path,style='path')}"
)
ANGULAR_PROJECT_GRAPH_CONSTRUCTED = f"{add_styletags_to_string('- Angular project graph constructed', style='success')} voyager keep going..."

"""
ASP predefined_phrases
"""

create_asp_prompt = lambda code: f"""
Migrate all the given code from ASP Classic to ASP .Net MVC. Separate the code into two distinct code blocks: 
one for the business logic named code.cs and another for the visual code (HTML) named code.cshtml. 
If the original code is written in VBScript, translate it to C#. 
Keep JScript in the HTML code to prevent injecting bugs into the output code. Ensure all code is migrated.
The code to migrate is as follows:
{code}
"""

"""
document predefined_phrases
"""

create_document_prompt = lambda code: f"""
"Create a comprehensive documentation for the code given in a new block code.
For that use the stadards, example if the code is in python use Pep8 
Your documentation should include a brief overview of the purpose of the file, 
explanations of any functions or classes defined within the file, descriptions of input parameters, 
return values, and any exceptions raised.
Do not forget to create the block code with the code documentated
The code to document is the follow:
{code}
"""