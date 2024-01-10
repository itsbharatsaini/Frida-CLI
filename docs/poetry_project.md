# FridaCLI poetry project

The FridaCLI project is build as a **python package configured** using `poetry` which is a python package that provides tools to easy **create, build, test and even publish** your python projects in PyPi. [(Poetry official documentation)](www.google.com)

So in order to contribute in the development of new features ir required to have `poetry` package installed in your system by running:

```bash
pip install poetry
```

## Dependencies

Any `poetry` project works thanks to a pair of files that stablish the **package info** and it's **dependencies specification**: `pyproject.toml` and `poetry.lock`.

#### Updating project dependencies

The poetry package includes a way to **manipulate the configuration files properly** by using commands. In case you want to **add a new dependency** to the project run this command:

```bash
poetry add <dependency>
```

If you want to **remove a dependency** run this other command:

```bash
poetry remove <dependency>
```

## Build and testing

#### Testing Frida package in your computer

The poetry tool provides the creation of a **virtual environment where you can test** the execution of your project. You do this by running:

```bash
poetry shell
```

If you are **located inside your poetry project** directory, this will create and activate a python virtual environment where now you can install your project by running:

```bash
poetry install
```

this will install the `frida` script in your system, you can test this by executing:

```bash
frida --help
```

#### Building Frida to install it in any computer

You may want to **test your new features** in diferent computers or python virtual environments. To do this, poetry provides the `build` command:

```bash
poetry build
```

This will create in your FridaCLI repository a new folder named `dist/`. Inside this directory there will be a pair of installable files:

```
./dist
|_ fridacli-0.1.0-py3-none-any.whl
|_ fridacli-0.1.0.tar.gz
```

You can use the `fridacli-0.1.0-py3-none-any.whl` file to install your FridaCLI build in your computer or any other device using a python virtual environment:

```bash
python -m venv frida
./frida/Scripts/activate # windows
source ./frida/bin/activate  # unix based OS
pip install fridacli-0.1.0-py3-none-any.whl
```

You can check that the frida script is installed correctly by executing:

```
frida --help
```
