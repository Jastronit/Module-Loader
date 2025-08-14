import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Hlavný obsah
        text_edit = QTextEdit("Hlavné okno (má byť nepriehľadné)")
        self.setCentralWidget(text_edit)

        # Dock widget
        self.dock = QDockWidget("Testovací Dock", self)
        self.dock.setWidget(QTextEdit("Dock widget (má byť polopriehľadný)"))
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        # Prvýkrát nastavíme polopriehľadnosť
        self.apply_translucent_background(self.dock, QColor(0, 255, 0, 127))  # zelená, alpha=127

        # Reakcia na oddokovanie
        self.dock.topLevelChanged.connect(self.on_dock_top_level_changed)

    def apply_translucent_background(self, widget, color: QColor):
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        p = widget.palette()
        p.setColor(QPalette.Base, color)
        widget.setPalette(p)
        widget.setAutoFillBackground(True)
        print(f"[DEBUG] Nastavená farba: {color.getRgb()}")

    def on_dock_top_level_changed(self, floating):
        if floating:
            print("[DEBUG] Dock bol oddokovaný → znovu nastavujem priehľadnosť")
            self.apply_translucent_background(self.dock, QColor(0, 255, 0, 127))
        else:
            print("[DEBUG] Dock bol zadokovaný")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
