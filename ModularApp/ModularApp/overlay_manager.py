from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
import os
import json

class OverlayManager:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.custom_overlays = self.load_custom_overlays()
        self.overlay_windows = {}

    def load_custom_overlays(self):
        path = os.path.join("modules", "Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3", "overlays", "custom_overlays.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_custom_overlays(self):
        path = os.path.join("modules", "Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3", "overlays", "custom_overlays.json")
        with open(path, "w") as f:
            json.dump(self.custom_overlays, f)

    def create_overlay(self, overlay_name, overlay_params):
        overlay_widget = QWidget()
        layout = QVBoxLayout(overlay_widget)
        overlay_widget.setLayout(layout)

        overlay_label = QLabel(f"Overlay: {overlay_name}")
        layout.addWidget(overlay_label)

        self.overlay_windows[overlay_name] = overlay_widget
        self.custom_overlays[overlay_name] = overlay_params
        self.save_custom_overlays()

        overlay_widget.show()

    def delete_overlay(self, overlay_name):
        if overlay_name in self.overlay_windows:
            self.overlay_windows[overlay_name].close()
            del self.overlay_windows[overlay_name]
            del self.custom_overlays[overlay_name]
            self.save_custom_overlays()

    def list_overlays(self):
        return list(self.custom_overlays.keys())

    def get_overlay_params(self, overlay_name):
        return self.custom_overlays.get(overlay_name, {})

def create_overlay_manager_widget():
    manager = OverlayManager()
    widget = QWidget()
    layout = QVBoxLayout(widget)

    overlay_list = QListWidget()
    layout.addWidget(overlay_list)

    def refresh_overlay_list():
        overlay_list.clear()
        overlay_list.addItems(manager.list_overlays())

    refresh_overlay_list()

    btn_create = QPushButton("Create Overlay")
    layout.addWidget(btn_create)

    btn_delete = QPushButton("Delete Selected Overlay")
    layout.addWidget(btn_delete)

    def create_overlay():
        overlay_name = f"Overlay_{len(manager.list_overlays()) + 1}"
        overlay_params = {"x": 100, "y": 100, "w": 400, "h": 300}
        manager.create_overlay(overlay_name, overlay_params)
        refresh_overlay_list()

    def delete_selected_overlay():
        selected_items = overlay_list.selectedItems()
        if selected_items:
            overlay_name = selected_items[0].text()
            manager.delete_overlay(overlay_name)
            refresh_overlay_list()

    btn_create.clicked.connect(create_overlay)
    btn_delete.clicked.connect(delete_selected_overlay)

    return widget