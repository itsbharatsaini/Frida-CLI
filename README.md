# Frida CLI 💻


With Frida CLI, you can easily create documentation for all your project files in just a few clicks.
 
But that's not all – Frida CLI also features a chat function that allows you to communicate directly with your project files. Need to discuss a specific piece of code or clarify a section of documentation? Simply chat with your files in real-time for seamless collaboration.
![image](https://github.com/Fridaplatform/Frida-CLI/assets/152227458/963e684b-fafa-451f-bdc5-3343c40dfb05)

## FridaCLI Setup and Executable Creation

Follow these steps to set up the project, install dependencies, and create a standalone executable file.

### General Setup
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

### Create the Executable 
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
## Configuration
Some configuration is required to start working.
First select the project you want to work on

![image](https://github.com/Fridaplatform/Frida-CLI/assets/152227458/f8356175-3ddd-4e72-b7a6-eff0e78903fa)
Secound write the LLMOPS key and the models you want to work on

![image](https://github.com/Fridaplatform/Frida-CLI/assets/152227458/0f134392-bc13-4373-b375-90683561a97a)

Last if you want to excute python code you need to select the Python environment
![image](https://github.com/Fridaplatform/Frida-CLI/assets/152227458/64a20a2e-6272-4789-a65a-0dfc67364fbc)



## Create documentation
To document your file, follow these steps:
  - Ensure the desired project is selected.
  - From the dropdown menu in the upper left corner of the screen, select the option "Generate Documentation."
  - Click the Execute button.
    
The following screen will appear:

![image](https://github.com/Fridaplatform/Frida-CLI/assets/152227458/b9b0ca97-7079-4e7d-8e66-445fb00b6533)

You can configure various parameters, including:

  - **Documentation Format**: Choose the format for the documentation.
  - **Save Path**: Specify the path where the documentation will be saved.
  - **Special Formatter**: Enable a special formatter (available for C# and Python only).
  - **Documentation Method** (model type):
    - Quick: The file is decomposed into functions, and each function is documented in parallel.
    - Slow: The file is processed in its entirety (Note: The file may be truncated due to the model's context window).
    
Once the documentation process is completed the following window will appear:

![MicrosoftTeams-image](https://github.com/Fridaplatform/Frida-CLI/assets/152227458/6314aeca-f8cd-447e-9109-09480d79a203)

If any errors are detected during the documentation process, they will be displayed along with the results. This ensures you can identify and address issues promptly, improving the overall accuracy and quality of the documentation.


