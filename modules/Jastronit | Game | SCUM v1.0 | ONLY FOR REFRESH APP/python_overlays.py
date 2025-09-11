# python_overlays.py
import os
import json
import glob
import importlib.util
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
import overlay_manager

CONFIG_FILE = "config/python_overlays.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE,"r") as f: return json.load(f)
        except: return {}
    return {}

def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE,"w") as f: json.dump(data,f,indent=2)

def create_widget(BaseClass,module_name):
    class PythonOverlaysWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            self.setWindowTitle("Python Overlays")
            layout=QVBoxLayout(self)
            self.setLayout(layout)
            self.list=QListWidget()
            layout.addWidget(self.list)
            self.btn_toggle=QPushButton("Toggle visibility (selected)")
            self.btn_toggle.clicked.connect(self.toggle_selected)
            layout.addWidget(self.btn_toggle)
            self.config = load_config()
            self.refresh_list()

        def refresh_list(self):
            self.list.clear()
            overlays_path=os.path.join("modules",module_name,"overlays")
            files = sorted(glob.glob(os.path.join(overlays_path,"*.py"))) if os.path.isdir(overlays_path) else []
            mgr=overlay_manager.start_overlay_manager()
            for f in files:
                name=os.path.splitext(os.path.basename(f))[0]
                item=QListWidgetItem(name)
                full_name=f"{module_name}:{name}"
                if full_name in mgr.overlays: win=mgr.overlays[full_name]; visible=getattr(win,'user_visible',True)
                else: visible=self.config.get(name,{}).get("user_visible",True)
                item.setCheckState(Qt.Checked if visible else Qt.Unchecked)
                self.list.addItem(item)

        def toggle_selected(self):
            items=self.list.selectedItems()
            if not items: return
            name=items[0].text()
            full_name=f"{module_name}:{name}"
            mgr=overlay_manager.start_overlay_manager()
            if full_name in mgr.overlays:
                win=mgr.overlays[full_name]
            else:
                # dynamicky load
                path=os.path.join("modules",module_name,"overlays",f"{name}.py")
                spec=importlib.util.spec_from_file_location(name,path)
                mod=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod,"create_overlay"): win=mod.create_overlay()
                else: return
                mgr.add_overlay(win,full_name,{"module_name":module_name})
            # toggle
            win.user_visible = not getattr(win,'user_visible',True)
            win.set_overlay_visible(win.user_visible and mgr.global_show)
            # save state
            self.config[name]=self.config.get(name,{})
            self.config[name]["user_visible"]=win.user_visible
            if hasattr(win,"geometry"):  # save size/position if supported
                geo=win.geometry()
                self.config[name]["x"]=geo.x(); self.config[name]["y"]=geo.y()
                self.config[name]["w"]=geo.width(); self.config[name]["h"]=geo.height()
            save_config(self.config)
            self.refresh_list()

    return PythonOverlaysWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1

