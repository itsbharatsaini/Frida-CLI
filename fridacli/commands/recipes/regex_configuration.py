CODE_FROM_ALL_EXTENSIONS = r"```(?:javascript|java|csharp|c#|C#|python)*(.*)```"
PARAM_CSHARP = r"^\s*<\s*param\s*name\s*=\s*\"([\w\s]*)\">([\w\.\-\s<>=\"/{}]*)</param>\s*$"
RETURN_CSHARP = r"^\s*<\s*returns\s*>([\w\.\-\s<>=\"/{}]*)</returns>\s*$"
EXCEPTION_CSHARP = r"^\s*<\s*exception\s*cref\s*=\s*\"([\w\s.]*)\">([\w\.\-\s<>=\"/{}]*)</exception>\s*$"