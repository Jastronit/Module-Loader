import os
import sys
import importlib.util
import threading
import subprocess
import platform
import atexit
import json

import gui_main

MODULES_DIR = "modules"

module_path = os.path.join(os.path.dirname(__file__), "modules")
if module_path not in sys.path:
    sys.path.append(module_path)

def load_custom_overlays():
    overlays_path = os.path.join(MODULES_DIR, "Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3", "overlays", "custom_overlays.json")
    if os.path.exists(overlays_path):
        with open(overlays_path, "r") as f:
            return json.load(f)
    return {}

def save_custom_overlays(overlays):
    overlays_path = os.path.join(MODULES_DIR, "Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3", "overlays", "custom_overlays.json")
    with open(overlays_path, "w") as f:
        json.dump(overlays, f)

def main():
    custom_overlays = load_custom_overlays()
    # Initialize overlays or any other logic here

    # Example of how to save overlays after modifications
    # save_custom_overlays(custom_overlays)

if __name__ == "__main__":
    main()