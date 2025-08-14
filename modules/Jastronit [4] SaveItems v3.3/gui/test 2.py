import sys
import configparser
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QTextEdit,
    QDialog, QFormLayout, QSpinBox, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QAction, QPalette

CONFIG_FILE = "config.ini"

class ColorSettingsDialog(QDialog):
    def __init__(self, parent=None, color=QColor(0,255,0,127)):
        super().__init__(parent)
        self.setWindowTitle("Nastavenie farby docku")
        self.color = color

        layout = QFormLayout()
        self.spin_r = QSpinBox()
        self.spin_r.setRange(0, 255)
        self.spin_r.setValue(color.red())
        layout.addRow("R:", self.spin_r)

        self.spin_g = QSpinBox()
        self.spin_g.setRange(0, 255)
        self.spin_g.setValue(color.green())
        layout.addRow("G:", self.spin_g)

        self.spin_b = QSpinBox()
        self.spin_b.setRange(0, 255)
        self.spin_b.setValue(color.blue())
        layout.addRow("B:", self.spin_b)

        self.spin_a = QSpinBox()
        self.spin_a.setRange(0, 255)
        self.spin_a.setValue(color.alpha())
        layout.addRow("A:", self.spin_a)

        btn_apply = QPushButton("Použiť")
        btn_apply.clicked.connect(self.apply)
        layout.addRow(btn_apply)

        self.setLayout(layout)

    def apply(self):
        self.color.setRed(self.spin_r.value())
        self.color.setGreen(self.spin_g.value())
        self.color.setBlue(self.spin_b.value())
        self.color.setAlpha(self.spin_a.value())
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo priehľadného docku")
        self.resize(800,600)

        # Hlavné okno
        self.setCentralWidget(QTextEdit("Hlavné okno (nepriehľadné)"))

        # Dock
        self.dock = QDockWidget("Dock", self)
        self.dock.setWidget(QTextEdit("Dock widget (polopriehľadný)"))
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.topLevelChanged.connect(self.on_dock_top_level_changed)

        # Načítať farbu z configu
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE)
        self.bg_color = self.read_color_from_config()

        # Nastaviť počiatočnú farbu
        self.apply_translucent_background(self.dock, self.bg_color)

        # Ikona nastavení farby
        action_color = QAction(QIcon(), "Nastaviť farbu docku", self)
        action_color.triggered.connect(self.open_color_dialog)
        self.menuBar().addAction(action_color)

    def read_color_from_config(self):
        try:
            r = int(self.config.get('Background', 'r'))
            g = int(self.config.get('Background', 'g'))
            b = int(self.config.get('Background', 'b'))
            a = int(self.config.get('Background', 'a'))
            print(f"[DEBUG] Načítaná farba z config: {r},{g},{b},{a}")
            return QColor(r,g,b,a)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            # Default farba
            return QColor(0,255,0,127)

    def save_color_to_config(self):
        if not self.config.has_section('Background'):
            self.config.add_section('Background')
        self.config.set('Background','r',str(self.bg_color.red()))
        self.config.set('Background','g',str(self.bg_color.green()))
        self.config.set('Background','b',str(self.bg_color.blue()))
        self.config.set('Background','a',str(self.bg_color.alpha()))
        with open(CONFIG_FILE, 'w') as f:
            self.config.write(f)
        print(f"[DEBUG] Farba uložená do config: {self.bg_color.getRgb()}")

    def apply_translucent_background(self, widget, color: QColor):
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        p = widget.palette()
        p.setColor(QPalette.Base, color)
        widget.setPalette(p)
        widget.setAutoFillBackground(True)
        print(f"[DEBUG] Nastavená farba: {color.getRgb()}")

    def on_dock_top_level_changed(self, floating):
        if floating:
            print("[DEBUG] Dock oddokovaný, znovu aplikujem farbu")
            self.apply_translucent_background(self.dock, self.bg_color)
        else:
            print("[DEBUG] Dock zadokovaný")

    def open_color_dialog(self):
        dlg = ColorSettingsDialog(self, self.bg_color)
        if dlg.exec():
            self.bg_color = dlg.color
            self.apply_translucent_background(self.dock, self.bg_color)
            self.save_color_to_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
