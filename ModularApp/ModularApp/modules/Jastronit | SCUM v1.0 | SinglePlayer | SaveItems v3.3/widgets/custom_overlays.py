from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout, QSpinBox
from PySide6.QtCore import Qt
import os
import json

class CustomOverlaysWidget(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.setLayout(QVBoxLayout())
        
        self.overlay_list = QListWidget()
        self.layout().addWidget(QLabel("Custom Overlays:"))
        self.layout().addWidget(self.overlay_list)
        
        self.load_overlays()

        btn_create = QPushButton("Create Overlay")
        btn_create.clicked.connect(self.create_overlay)
        self.layout().addWidget(btn_create)

        btn_delete = QPushButton("Delete Selected Overlay")
        btn_delete.clicked.connect(self.delete_selected_overlay)
        self.layout().addWidget(btn_delete)

    def load_overlays(self):
        overlays_path = os.path.join("modules", self.module_name, "overlays", "custom_overlays.json")
        if os.path.exists(overlays_path):
            with open(overlays_path, "r") as f:
                overlays = json.load(f)
                for overlay in overlays:
                    self.overlay_list.addItem(overlay)

    def save_overlays(self):
        overlays_path = os.path.join("modules", self.module_name, "overlays", "custom_overlays.json")
        overlays = [self.overlay_list.item(i).text() for i in range(self.overlay_list.count())]
        with open(overlays_path, "w") as f:
            json.dump(overlays, f)

    def create_overlay(self):
        overlay_name = f"CustomOverlay_{len(self.overlay_list) + 1}"
        self.overlay_list.addItem(overlay_name)
        self.save_overlays()

    def delete_selected_overlay(self):
        selected_item = self.overlay_list.currentItem()
        if selected_item:
            self.overlay_list.takeItem(self.overlay_list.row(selected_item))
            self.save_overlays()