import os
import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class CustomOverlaysManager(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.setWindowTitle("Custom Overlays Manager")
        layout = QVBoxLayout(self)

        self.overlay_list = QListWidget()
        layout.addWidget(QLabel("Custom Overlays:"))
        layout.addWidget(self.overlay_list)

        self.load_overlays()

        btn_create = QPushButton("Create Overlay")
        btn_create.clicked.connect(self.create_overlay)
        layout.addWidget(btn_create)

        btn_delete = QPushButton("Delete Selected Overlay")
        btn_delete.clicked.connect(self.delete_selected_overlay)
        layout.addWidget(btn_delete)

        self.refresh_overlay_list()

    def load_overlays(self):
        self.overlays = {}
        overlays_file = os.path.join("modules", self.module_name, "overlays", "custom_overlays.json")
        if os.path.exists(overlays_file):
            with open(overlays_file, "r") as f:
                self.overlays = json.load(f)

    def save_overlays(self):
        overlays_file = os.path.join("modules", self.module_name, "overlays", "custom_overlays.json")
        with open(overlays_file, "w") as f:
            json.dump(self.overlays, f)

    def refresh_overlay_list(self):
        self.overlay_list.clear()
        for overlay_name in self.overlays.keys():
            self.overlay_list.addItem(overlay_name)

    def create_overlay(self):
        overlay_name = f"CustomOverlay_{len(self.overlays) + 1}"
        self.overlays[overlay_name] = {
            "widgets": [],
            "position": {"x": 100, "y": 100, "w": 400, "h": 300}
        }
        self.save_overlays()
        self.refresh_overlay_list()

    def delete_selected_overlay(self):
        selected_item = self.overlay_list.currentItem()
        if selected_item:
            overlay_name = selected_item.text()
            del self.overlays[overlay_name]
            self.save_overlays()
            self.refresh_overlay_list()

def create_widget(BaseClass, module_name):
    return CustomOverlaysManager(module_name)

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1