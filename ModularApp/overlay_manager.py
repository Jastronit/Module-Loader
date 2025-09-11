# filepath: /home/jastronit/Plocha/python/SCUM/ModularApp/modules/Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3/widgets/custom_overlays.py
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QHBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt

def create_widget(BaseClass, module_name):
    class CustomOverlaysWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            # --- Overlay zoznam ---
            layout.addWidget(QLabel("Custom Overlays:"))
            self.overlay_list = QListWidget()
            layout.addWidget(self.overlay_list)
            self.load_custom_overlays()

            # --- Pridanie ovládacích prvkov ---
            btn_create = QPushButton("Create Overlay")
            btn_create.clicked.connect(self.create_overlay)
            layout.addWidget(btn_create)

            btn_delete = QPushButton("Delete Selected Overlay")
            btn_delete.clicked.connect(self.delete_selected_overlay)
            layout.addWidget(btn_delete)

            self.overlay_name_input = QSpinBox()
            layout.addWidget(self.overlay_name_input)

        def load_custom_overlays(self):
            self.overlay_list.clear()
            config_path = self.get_config_path("custom_overlays.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    overlays = json.load(f)
                    for overlay in overlays:
                        self.overlay_list.addItem(overlay)

        def create_overlay(self):
            overlay_name = f"Overlay_{len(self.overlay_list) + 1}"
            self.overlay_list.addItem(overlay_name)
            self.save_custom_overlay(overlay_name)

        def delete_selected_overlay(self):
            selected = self.overlay_list.currentItem()
            if selected:
                overlay_name = selected.text()
                self.overlay_list.takeItem(self.overlay_list.row(selected))
                self.remove_custom_overlay(overlay_name)

        def save_custom_overlay(self, overlay_name):
            config_path = self.get_config_path("custom_overlays.json")
            overlays = []
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    overlays = json.load(f)
            overlays.append(overlay_name)
            with open(config_path, "w") as f:
                json.dump(overlays, f)

        def remove_custom_overlay(self, overlay_name):
            config_path = self.get_config_path("custom_overlays.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    overlays = json.load(f)
                overlays.remove(overlay_name)
                with open(config_path, "w") as f:
                    json.dump(overlays, f)

        def get_config_path(self, filename):
            return os.path.join("modules", self.module_name, "config", filename)

    return CustomOverlaysWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1