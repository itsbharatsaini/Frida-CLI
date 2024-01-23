# 📦Commands package

Package that contains the source **code executed as commands** by the `frida` CLI application.

## Chat command

Module that contains the functions executed during the chat session loop of the `frida chat` command. This module handles the requests made to the **softtek SDK** and the execution of the **[chat subcommands]()** source code.

This module is used in the CLI app main file by calling the function `exec_chat`.

## Config command

Module that contains the source code executed by the `frida config` command. Contains functions that can **create, read and overwrite** the configuration file `.fridacli`.

This module is used in the CLI app main file by calling the function `exec_config`.
