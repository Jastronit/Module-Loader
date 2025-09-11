from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
import os
import json

class OverlaysManager(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.setWindowTitle("Overlays Manager")
        layout = QVBoxLayout(self)

        self.overlay_list = QListWidget()
        layout.addWidget(QLabel("Available Overlays:"))
        layout.addWidget(self.overlay_list)

        self.load_overlays()

        btn_delete = QPushButton("Delete Selected Overlay")
        btn_delete.clicked.connect(self.delete_selected_overlay)
        layout.addWidget(btn_delete)

        btn_copy = QPushButton("Copy Selected Overlay")
        btn_copy.clicked.connect(self.copy_selected_overlay)
        layout.addWidget(btn_copy)

        self.setLayout(layout)

    def load_overlays(self):
        overlays_dir = os.path.join("modules", self.module_name, "overlays")
        if os.path.exists(overlays_dir):
            overlays = [f for f in os.listdir(overlays_dir) if f.endswith(".py")]
            self.overlay_list.addItems(overlays)

    def delete_selected_overlay(self):
        selected_item = self.overlay_list.currentItem()
        if selected_item:
            overlay_name = selected_item.text()
            overlay_path = os.path.join("modules", self.module_name, "overlays", overlay_name)
            if os.path.exists(overlay_path):
                os.remove(overlay_path)
                self.overlay_list.takeItem(self.overlay_list.row(selected_item))
                self.save_overlay_positions()

    def copy_selected_overlay(self):
        selected_item = self.overlay_list.currentItem()
        if selected_item:
            overlay_name = selected_item.text()
            src_path = os.path.join("modules", self.module_name, "overlays", overlay_name)
            dst_path = os.path.join("modules", self.module_name, "overlays", f"copy_of_{overlay_name}")
            if os.path.exists(src_path):
                with open(src_path, 'r') as src_file:
                    content = src_file.read()
                with open(dst_path, 'w') as dst_file:
                    dst_file.write(content)
                self.overlay_list.addItem(f"copy_of_{overlay_name}")

    def save_overlay_positions(self):
        overlay_positions = {}
        for index in range(self.overlay_list.count()):
            overlay_name = self.overlay_list.item(index).text()
            overlay_positions[overlay_name] = {
                "position": self.overlay_list.item(index).data(Qt.UserRole),
                "size": self.overlay_list.item(index).data(Qt.UserRole + 1)
            }
        with open(os.path.join("modules", self.module_name, "overlays", "overlays.json"), 'w') as f:
            json.dump(overlay_positions, f)

def create_widget(BaseClass, module_name):
    return OverlaysManager(module_name)

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1