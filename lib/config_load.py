import os
import sys
from pathlib import Path
import importlib.util


def load():
    """if config.py is present in the config directory,
    load that in place of the usual relative config.py"""
    if sys.platform == "win32":
        config_dir = os.path.join(Path.home(), "AppData", "Roaming", "filerift")
    else:
        config_dir = os.path.join(Path.home(), ".config", "filerift")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.py")
    force_local_config = os.path.exists("./.filerift_force_local_config")
    if not os.path.exists(config_path) or force_local_config:
        config_path = "config.py"
        if not os.path.exists(config_path):
            with open("config.py", "w") as file:
                file.write("")
    spec = importlib.util.spec_from_file_location("config", config_path)
    if spec != None:
        config = importlib.util.module_from_spec(spec)
        if spec.loader != None:
            spec.loader.exec_module(config)
            sys.modules["config"] = config
