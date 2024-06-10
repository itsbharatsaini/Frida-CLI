# FridaCLI Setup and Executable Creation

Follow these steps to set up the project, install dependencies, and create a standalone executable file.

## General Setup
1. **Clone the repository**

   ```sh
   git clone https://github.com/Fridaplatform/Frida-CLI.git
2. **Access the path via terminal**

    ```sh
    cd your-repository-folder
3. **Install all the packages in the requirements.txt (preferably in a venv)**

    It is recommended to create and activate a virtual environment before installing the packages.

    ```sh
    # Create venv file (the ".venv" is just a name for the folder, if you change it the next command will need to start with the same name)
    python -m venv .venv
    ```
    ```sh
    # Initiate virtual environment
    .venv/Scripts/activate
    ```
    ```sh
    # Install the dependencies
    pip install requirements.txt
    ```
4. **You can now manually run FridaCLI**

    Just execute the main file ╰(*°▽°*)╯

    ```sh
    python main.py
    ```

## Create the Executable 
1. **Install PyInstaller**
    
    Use the same virtual environment (if you used one)

    ```sh
    pip install pyinstaller
2. **Run the following command**

    This command has everything needed for this project to be compiled into a .exe file.

    ```sh
    pyinstaller --onefile -p "C:\[CompleteThePath]\Frida-CLI\.venv\Lib\site-packages" --collect-submodules textual --hidden-import pinecone --add-data "C:\[CompleteThePath]\Frida-CLI\fridacli;fridacli" --add-data "C:\[CompleteThePath]\Frida-CLI\fridacli\gui\tcss\frida_styles.tcss;fridacli/gui/tcss" main.py --collect-all pinecone --clean
    ```
    Don't forget to complete the Path with yours in **[CompleteThePath]** sections.
3. **Locate the executable**

    After running the PyInstaller command, a folder named dist will be created in the repository directory. Inside this folder, you will find:

    * **main.exe**: The standalone executable file.
    * **app.txt**: The installation logs.

    Now, you can just double-click the executable file to run FridaCLI! (●'◡'●)

    **Important Note:** The executable works better using the new windows terminal, you can force it to execute with it using this command:

    ```sh
    start wt.exe -d "COMPLETE_PATH/main.exe"
    ```
