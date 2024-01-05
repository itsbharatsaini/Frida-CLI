from InquirerPy import get_style
from rich.theme import Theme

# FridaCLI's Color palette
WHITE = "#F6F0ED"
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
    "bot": f"{CYAN}",
    "command": f"{ORANGE} bold",
    "code": f"bold white on {DARK_GRAY}",
    "error": f"{RED} italic",
    "highlight": f"{PINK} bold",
    "info": f"{GRAY}",
    "link": f"{BLUE_1} italic",
    "option": f"{YELLOW}",
    "operation": f"{BLUE_2} bold",
    "path": f"{BLUE_1} bold",
    "process": f"{GRAY} italic",
    "success": f"{GREEN} italic",
    "system": f"{WHITE}",
    "user": f"{AQUAMARINE}",
    "warning": f"{YELLOW} italic",
}

# Frida's default Rich console theme
console_theme = Theme(color_palette)

# Inquirer user input styles
user_style = color_palette["user"]
folder_style = color_palette["info"]
open_folder_style = color_palette["path"]
password_style = color_palette["info"]
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
basic_style = get_style(
    {
        "question": WHITE,
        "answered_question": WHITE,
        "input": password_style,
        "answer": password_style,
    }
)
