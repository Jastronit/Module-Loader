from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import QTimer, Qt
import os

class OverlayConsole(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.label = QLabel("Console Overlay")
        layout.addWidget(self.label)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(1000)  # Refresh every second

        self.show_mode = False  # Initially not showing

    def set_show_mode(self, show):
        self.show_mode = show
        if show:
            self.refresh_data()  # Load data when showing

    def refresh_data(self):
        if not self.show_mode:
            return

        log_file = self.get_data_path("log.txt")
        log_lines = []

        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                log_lines = f.readlines()[-64:]  # Last 64 lines

        self.text_edit.clear()
        for line in log_lines:
            self.text_edit.append(line.strip())

    def get_data_path(self, filename):
        return os.path.join("modules", self.module_name, "data", filename)