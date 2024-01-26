# 📦Interface package

Package in charge of providing the **user interface functionalities** to the rest of the system packages, the different modules work together through the main file: `console`.

## Console

Module containing the `Console` class that uses the **rich** library to provide functionality for input and output of stylized data on the terminal in a simple way.

This class inherits its basic functionalities and attributes to the child classes: `SystemConsole`, `UserConsole` and `BotConsole`.

#### System Console class

Child class that inherits from `Console` the ability to perform input and outputs but implementing its own functionalities for **display information that is neither provided by the user nor by the AI assitant but as the system itself.**

This class provides features such as:

- Print centered notification messages
- Confirm user action with (y/N) options
- Print a panel
- Receive a secret password as an input

#### User Console class

Child class that inherits from `Console` the ability to perform input and outputs but implementing its own functionalities for **formatting the user inputs and display information about the current state of the user session.**

This class provides features such as:

- Display user's username as user's input message.
- Apply color to the text written by the user.
- Display information about the current directory and its status.

#### Bot Console class

Child class that inherits from `Console` the ability to perform input and outputs but implementing its own functionalities for **formatting the AI assistant responses and processing code blocks.**

This class provides features such as:

- Apply color to the text printed by the bot
- Apply Markdown format to codeblocks

## Styles

Contains functions that **handles and applies styles** to visual elements displayed on screen. This module does things like:

- Apply a specific style tag to a string
- Apply style tags to a string based on predefined regex patterns
- Turn a **pandas** `dataframe` into a **rich** `Table` object

## Theme

Contains string constants that represent the **Frida's CLI system color palette**. These are used to create a **rich** `Theme` object that is used as default in the `console` module.
