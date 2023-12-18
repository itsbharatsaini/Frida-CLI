from rich.theme import Theme

# FridaCLI's Colour palette
GRAY = "rgb(100,101,104)"
DARK_GRAY = "#222222"
RED = "rgb(235,0,44)"
GREEN = "rgb(150,235,0)"
YELLOW = "rgb(235,235,0)"
ORANGE = "rgb(235,129,0)"
CYAN = "rgb(0,235,235)"
BLUE_1 = "rgb(0,129,235)"
BLUE_2 = "rgb(86,0,235)"
PINK = "rgb(235,0,235)"
AQUAMARINE = "rgb(0,235,159)"

# Frida's default console theme
console_theme = Theme(
    {
        "info": f"{GRAY}",
        "bot": f"{CYAN}",
        "user": f"{AQUAMARINE}",
        "command": f"{ORANGE} bold",
        "option": f"{YELLOW}",
        "operation": f"{BLUE_2} bold",
        "warning": f"{YELLOW} italic",
        "error": f"{RED} italic",
        "success": f"{GREEN} italic",
        "link": f"{BLUE_1} italic",
        "highlight": f"{PINK} bold",
        "code": f"bold white on {DARK_GRAY}",
    }
)
