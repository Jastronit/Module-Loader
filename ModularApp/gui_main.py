# filepath: /home/jastronit/Plocha/python/SCUM/ModularApp/modules/Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3/widgets/custom_overlays.py
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QHBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt
import overlay_manager

class CustomOverlaysWidget(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.overlay_list = QListWidget()
        self.layout.addWidget(QLabel("Custom Overlays:"))
        self.layout.addWidget(self.overlay_list)
        self.refresh_overlay_list()

        self.layout.addWidget(QLabel("Overlay Position:"))
        self.spin_x = QSpinBox(); self.spin_x.setRange(0, 1920); self.spin_x.setValue(100)
        self.spin_y = QSpinBox(); self.spin_y.setRange(0, 1080); self.spin_y.setValue(100)
        self.layout.addWidget(self.spin_x)
        self.layout.addWidget(self.spin_y)

        btn_create = QPushButton("Create Overlay")
        btn_create.clicked.connect(self.create_overlay)
        self.layout.addWidget(btn_create)

        btn_delete = QPushButton("Delete Overlay")
        btn_delete.clicked.connect(self.delete_selected_overlay)
        self.layout.addWidget(btn_delete)

    def refresh_overlay_list(self):
        self.overlay_list.clear()
        overlays = self.load_custom_overlays()
        for overlay in overlays:
            self.overlay_list.addItem(overlay)

    def create_overlay(self):
        overlay_name = f"Overlay_{len(self.overlay_list)}"
        overlay_data = {
            "name": overlay_name,
            "x": self.spin_x.value(),
            "y": self.spin_y.value(),
            "widget": "console"  # Môžeš pridať logiku na výber widgetu
        }
        overlays = self.load_custom_overlays()
        overlays.append(overlay_data)
        self.save_custom_overlays(overlays)
        self.refresh_overlay_list()

    def delete_selected_overlay(self):
        selected = self.overlay_list.currentItem()
        if selected:
            overlays = self.load_custom_overlays()
            overlays = [o for o in overlays if o["name"] != selected.text()]
            self.save_custom_overlays(overlays)
            self.refresh_overlay_list()

    def load_custom_overlays(self):
        config_path = os.path.join("modules", self.module_name, "config", "custom_overlays.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return []

    def save_custom_overlays(self, overlays):
        config_path = os.path.join("modules", self.module_name, "config", "custom_overlays.json")
        with open(config_path, "w") as f:
            json.dump(overlays, f, indent=2)

def create_widget(BaseClass, module_name):
    return CustomOverlaysWidget(module_name)

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1