from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPixmap, QPalette
import os
import json

def is_dark_mode():
    palette = QApplication.instance().palette()
    window_color = palette.color(QPalette.Window)
    return window_color.lightness() < 128

class ConsoleWidget(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.setMinimumSize(333, 100)

        if is_dark_mode():
            banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners/CONSOLE.png")
        else:
            banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners/CONSOLE_DARK.png")
        if os.path.exists(banner_path):
            self.banner = QLabel()
            pixmap = QPixmap(banner_path)
            self.banner.setAlignment(Qt.AlignCenter)
            self.banner.setPixmap(pixmap.scaledToHeight(32, Qt.SmoothTransformation))
            layout.addWidget(self.banner)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_widget)
        self.timer.start(1000)

        self.load_custom_overlays()

    def update_widget(self):
        log_file = self.get_data_path("log.txt")
        log_lines = []

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                log_lines = f.readlines()[-64:]

        self.text.clear()
        for line in log_lines:
            self.text.append(line.strip())

    def load_custom_overlays(self):
        overlays_file = os.path.join("modules", self.module_name, "overlays", "custom_overlays.json")
        if os.path.exists(overlays_file):
            with open(overlays_file, "r", encoding="utf-8") as f:
                overlays_data = json.load(f)
                # Load overlays data into the console or manage them as needed

    def get_data_path(self, filename):
        return os.path.join("modules", self.module_name, "data", filename)

    def close_widget(self):
        self.timer.stop()
        self.text.clear()