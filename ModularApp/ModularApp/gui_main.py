from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QScrollArea, QDockWidget, QPushButton
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
import os
import sys
import importlib.util
import overlay_manager
import json

# Cesta k priečinku s modulmi
module_path = "modules"

def load_modules(module_path):
    modules = {}
    if not os.path.exists(module_path):
        os.makedirs(module_path)

    for module_name in os.listdir(module_path):
        module_dir = os.path.join(module_path, module_name)
        if os.path.isdir(module_dir):
            modules[module_name] = []
    return modules

modules = load_modules(module_path)

class BaseWidget(QWidget):
    def __init__(self, module_name=None):
        super().__init__()
        self.module_name = module_name

    def get_config_path(self, filename):
        return os.path.join("modules", self.module_name, "config", filename)

    def get_data_path(self, filename):
        return os.path.join("modules", self.module_name, "data", filename)

    def update_widget(self):
        pass

    def close_widget(self):
        pass

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(1500, 800)
        self.setWindowTitle("Overlay Manager")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.image_label = QLabel()
        pixmap = QPixmap(480, 320)
        pixmap.fill(Qt.lightGray)
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(480, 320)
        left_layout.addWidget(self.image_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.list_widget = QListWidget()
        self.list_widget.addItems(modules.keys())
        scroll_area.setWidget(self.list_widget)
        scroll_area.setFixedWidth(480)

        left_layout.addWidget(scroll_area)
        main_layout.addWidget(left_panel)

        discord_link = QLabel('<a href="https://discord.gg/cqg6dDj5pW">💬 Discord: Join our community!</a>')
        discord_link.setOpenExternalLinks(True)

        coffee_link = QLabel('<a href="https://buymeacoffee.com/jastronit">☕ Buy me a coffee!</a>')
        coffee_link.setOpenExternalLinks(True)

        left_layout.addWidget(discord_link)
        left_layout.addWidget(coffee_link)

        self.right_dock = RightDockArea(image_label=self.image_label)
        main_layout.addWidget(self.right_dock)

        self.list_widget.currentTextChanged.connect(self.right_dock.load_widgets)

    def closeEvent(self, event):
        return super().closeEvent(event)

class RightDockArea(QMainWindow):
    def __init__(self, image_label):
        super().__init__()
        self.setFixedWidth(1000)
        self.setContentsMargins(0, 0, 0, 0)
        self.setDockNestingEnabled(True)

        self.image_label = image_label

    def load_widgets(self, module_name):
        img_path = os.path.join(module_path, module_name, "assets", "pictures", "480x320.png")
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.image_label.setPixmap(pixmap.scaled(480, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            pixmap = QPixmap(480, 320)
            pixmap.fill(Qt.lightGray)
            self.image_label.setPixmap(pixmap)

        for dock in self.findChildren(QDockWidget):
            self.removeDockWidget(dock)
            dock.setParent(None)

        module_dir = os.path.join(module_path, module_name, "widgets")
        if not os.path.exists(module_dir):
            return print(f"Module {module_name} has no widgets.")

        grouped_by_area = {}
        for fname in os.listdir(module_dir):
            if not fname.endswith(".py"):
                continue

            file_path = os.path.join(module_dir, fname)
            widget_name = os.path.splitext(fname)[0]

            mod_key = f"{module_name}.{widget_name}"
            spec = importlib.util.spec_from_file_location(mod_key, file_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_key] = mod
            spec.loader.exec_module(mod)

            widget = None
            if hasattr(mod, "create_widget"):
                widget = mod.create_widget(BaseWidget, module_name)
            elif hasattr(mod, "Widget"):
                widget = mod.Widget(module_name)
            if widget is None:
                continue

            area, order = Qt.RightDockWidgetArea, 1000
            if hasattr(mod, "get_widget_dock_position"):
                pos = mod.get_widget_dock_position()
                if isinstance(pos, tuple) and len(pos) >= 2:
                    area, order = pos[0], pos[1]
                else:
                    area = pos

            grouped_by_area.setdefault(area, []).append((order, widget_name, widget))

        for area, items in grouped_by_area.items():
            items.sort(key=lambda t: (t[0], t[1]))

            anchors = {}
            last_anchor = None

            for order, widget_name, widget in items:
                dock = QDockWidget(widget_name, self)
                dock.setObjectName(f"{module_name}:{widget_name}")
                dock.setAllowedAreas(Qt.AllDockWidgetAreas)
                dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
                dock.setWidget(widget)

                self.addDockWidget(area, dock)

                if order in anchors:
                    self.tabifyDockWidget(anchors[order], dock)
                else:
                    if last_anchor is not None:
                        self.splitDockWidget(last_anchor, dock, Qt.Vertical)
                    anchors[order] = dock
                    last_anchor = dock

def main(on_close_callback=None):
    app = QApplication(sys.argv)

    window = MainApp()

    manager = overlay_manager.start_overlay_manager()

    def handle_close(event):
        overlay_manager.stop_overlay_manager()
        if on_close_callback:
            try:
                on_close_callback()
            except Exception as e:
                print(f"Error calling on_close_callback: {e}")
        event.accept()

    window.closeEvent = handle_close
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()