# Frida CLI

**FridaCLI** is a **command line application powered by AI** developed by the innovation team at Softtek.

By installing this package on your device you can run a script that starts a chat session with your new personal peer programming AI assistant.

## Installation

Create a **python virtual environment** to install the FridaCLI package.

```bash
python -m venv <name>
./name/Scripts/activate # windows
source ./name/bin/activate  # unix based OS
```

Run the following **pip command** to install the current stable version of FridaCLI package.

```bash
pip install git+https://github.com/Fridaplatform/Frida-CLI.git@v0.2.0
```

## Usage

#### CLI's configuration

First configure **the API** key by executing this command:

```bash
frida config
```

Adittionaly you can check that te configuration variables are configured correctly by running the following command:

```bash
frida config --list
```

#### Chat with Frida

Now you can a chat session with your personal FridaCLI AI assitant by executing:

```bash
frida chat
```

![frida chat](assets/gifs/frida%20chat.gif)

You can use your programming project as context for Frida by loading your files using the following subcommand:

```bash
!open <directory_path>
```

By doing this you'll be able to **do peer programming with Frida** asking questions about the content of your source code files.

You can aks her for recomendations for refactoring, documentation, error detection, bug solving or just ask her for about any programming related question.

#### Chat commands

As a CLI, Frida counts with many utilities powered by AI that you can use to enrich your experience. Execute `!help` to see the list of available in-chat commands or checkout the [in-chat commands]() documentation.

![!help command](assets/gifs/help%20command.gif)
