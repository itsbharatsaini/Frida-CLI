# 📦Commands package

Package that contains the source **code executed as commands** by the `frida` CLI application.

## Chat callbacks

Module that contains the **functions executed as subcommands** in a chat session created with the `frida chat` command. This module contains the main features that are executable inside a chat session with the AI assistant, such as:

- Open a file directory and give the AI assistant context of its content.
- Document an entire folder directory.
- Display a tree view of the open directory.

## Chat command

This module is used in the CLI app main file by calling the function `exec_chat`.

## Config command

Module that contains the source code executed by the `frida config` command. Contains functions that can **create, read and write over** the configuration file `.fridacli`.

This module is used in the CLI app main file by calling the function `exec_config`.
