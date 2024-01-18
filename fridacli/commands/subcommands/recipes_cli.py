from fridacli.commands.recipes.angular_voyager import exec_angular_voyager
import os

def angular_voyager(args = None):
    """
    Recipe that migrates a angular project from an old version to a new version
    """
    path = args if args is not None else os.getcwd()
    exec_angular_voyager(path)
