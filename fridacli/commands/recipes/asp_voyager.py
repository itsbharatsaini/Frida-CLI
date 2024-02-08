
def exec_asp_voyager(file_manager, chatbot_agent, chatbot_console):
    files = file_manager.get_files()
    for file in files:
        code = open_file(file)
        prompt = f"""
Migrate all the given code from ASP Classic to ASP .Net MVC. Separate the code into two distinct code blocks: 
one for the business logic named code.cs and another for the visual code (HTML) named code.cshtml. 
If the original code is written in VBScript, translate it to C#. 
Keep JScript in the HTML code to prevent injecting bugs into the output code. Ensure all code is migrated.
The code to migrate is the follow:
\n
{code}
"""
        response = chatbot_agent.chat(prompt, True)
        print(response)
        chatbot_console.response(response)
        
def open_file(path):
    #print("opening...")
    with open(path, "r") as f:
        code = f.read()
        #print(code)
        return code