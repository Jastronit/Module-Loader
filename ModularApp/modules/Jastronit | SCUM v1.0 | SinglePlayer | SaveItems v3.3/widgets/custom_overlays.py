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

            # --- Pridanie a odstránenie overlayov ---
            btn_add = QPushButton("Add Overlay")
            btn_add.clicked.connect(self.add_overlay)
            layout.addWidget(btn_add)

            btn_delete = QPushButton("Delete Selected Overlay")
            btn_delete.clicked.connect(self.delete_selected_overlay)
            layout.addWidget(btn_delete)

            self.selected_overlay = None

        def load_custom_overlays(self):
            config_path = self.get_config_path("custom_overlays.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    overlays = json.load(f)
                    self.overlay_list.addItems(overlays)

        def add_overlay(self):
            overlay_name = f"Overlay_{len(self.overlay_list)}"
            self.overlay_list.addItem(overlay_name)
            self.save_custom_overlays()

        def delete_selected_overlay(self):
            selected = self.overlay_list.currentItem()
            if selected:
                self.overlay_list.takeItem(self.overlay_list.row(selected))
                self.save_custom_overlays()

        def save_custom_overlays(self):
            overlays = [self.overlay_list.item(i).text() for i in range(self.overlay_list.count())]
            config_path = self.get_config_path("custom_overlays.json")
            with open(config_path, "w") as f:
                json.dump(overlays, f, indent=2)

    return CustomOverlaysWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1