from InquirerPy import get_style
from rich.theme import Theme

# FridaCLI's Color palette
GRAY = "#646568"
DARK_GRAY = "#222222"
RED = "#eb002c"
GREEN = "#96eb00"
YELLOW = "#ebeb00"
ORANGE = "#eb8100"
CYAN = "#00ebeb"
BLUE_1 = "#0081eb"
BLUE_2 = "#5600eb"
PINK = "#eb00eb"
AQUAMARINE = "#00eb9f"
color_palette = {
    "system": f"{GRAY}",
    "process": f"{GRAY} italic",
    "bot": f"{CYAN}",
    "user": f"{AQUAMARINE}",
    "command": f"{ORANGE} bold",
    "option": f"{YELLOW}",
    "operation": f"{BLUE_2} bold",
    "warning": f"{YELLOW} italic",
    "error": f"{RED} italic",
    "success": f"{GREEN} italic",
    "path": f"{BLUE_1} bold",
    "link": f"{BLUE_1} italic",
    "highlight": f"{PINK} bold",
    "code": f"bold white on {DARK_GRAY}",
}

# Frida's default Rich console theme
console_theme = Theme(color_palette)

# Inquirer user input styles
user_style = color_palette["user"]
folder_style = color_palette["system"]
open_folder_style = color_palette["path"]
user_input_style = get_style(
    {
        "questionmark": folder_style,
        "answermark": folder_style,
        "question": user_style,
        "answered_question": user_style,
        "input": user_style,
        "answer": user_style,
    }
)
user_input_style_active_project = get_style(
    {
        "questionmark": open_folder_style,
        "answermark": open_folder_style,
        "question": user_style,
        "answered_question": user_style,
        "input": user_style,
        "answer": user_style,
    }
)
