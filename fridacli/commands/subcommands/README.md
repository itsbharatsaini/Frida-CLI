# 📦Subcommands package

Module that contains the **code executed as [in-chat commands]()** in a chat session created with the `frida chat` command. This module contains the main features that are executable inside a chat session with the AI assistant.

#### Callbacks

Module that contains a **reference to the source code** executed by every single **[in-chat command]()**. This module also handles the commands autocompletion options in order to import and use them within the `chat` command.

#### Subcommands Info

Module that contains the description and examples of usage of every single **[in-chat command]()**. This is the info used by the `!help` subcommand to print the available commands table.

#### Basic CLI

Module with functionalities and source code executed by the basic subcommands such as:

- `!exit`
- `!help`
- `!cd`
- `!ls`
- `!pwd`

#### Files CLI

Module with functionalities and source code executed by the `!open` and `!close` command that preprocess a the content of a specified directory.

#### Recipes CLI
