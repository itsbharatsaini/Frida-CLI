# 📦Interface package

Package in charge of providing the **user interface functionalities** to the rest of the system packages, the different modules work together through the main file: `console`.

## Console

Module containing the `Console` class that uses the **rich** library to provide functionality for input and output of stylized data on the terminal in a simple way.

This class is imported and used in the modules of the `commands` package _(chat, config, etc....)_ so that each command can use the styled data output features.

## Styles

Contains functions that **handles and applies styles** to visual elements displayed on screen. This module does things like:

- Apply a specific style tag to a string
- Apply style tags to a string based on predefined regex patterns
- Turn a **pandas** `dataframe` into a **rich** `Table` object

## Theme

Contains string constants that represent the **Frida's CLI system color palette**. These are used to create a **rich** `Theme` object that is used as default in the `console` module.
