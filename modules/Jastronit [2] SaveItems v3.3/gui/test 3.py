import sys
import configparser
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

CONFIG_FILE = "config.ini"

# --- Pomocné funkcie pre config ---
def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if "Background" not in config:
        config["Background"] = {"r": "0", "g": "255", "b": "0", "a": "127"}
    return config

# --- Hlavné okno ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Hlavné okno (nepriehľadné)
        text_edit = QTextEdit("Hlavné okno (nepriehľadné)")
        self.setCentralWidget(text_edit)

        # Dock widget
        self.dock = QDockWidget("Dock Widget", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        # Obsah docku
        dock_content = QTextEdit("Obsah dock widgetu")
        self.dock.setWidget(dock_content)

        # Načítanie farby z config.ini
        config = load_config()
        r = int(config["Background"]["r"])
        g = int(config["Background"]["g"])
        b = int(config["Background"]["b"])
        a = int(config["Background"]["a"])
        self.dock_color = QColor(r, g, b, a)

        # Aplikovanie priehľadnosti pri oddokovaní
        self.dock.topLevelChanged.connect(self.on_dock_top_level_changed)
        if self.dock.isFloating():
            self.apply_translucent_background(self.dock, self.dock_color)

    # Funkcia pre priehľadné pozadie docku
    def apply_translucent_background(self, widget, color: QColor):
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        p = widget.palette()
        p.setColor(QPalette.Base, color)
        widget.setPalette(p)
        widget.setAutoFillBackground(True)
        print(f"[DEBUG] Dock farba: {color.getRgb()}")

    # Pri oddokovaní
    def on_dock_top_level_changed(self, floating):
        if floating:
            print("[DEBUG] Dock oddokovaný → aplikuje sa priehľadnosť")
            self.apply_translucent_background(self.dock, self.dock_color)
        else:
            print("[DEBUG] Dock zadokovaný → nepriehľadný obsah zostáva")

# --- Spustenie aplikácie ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
