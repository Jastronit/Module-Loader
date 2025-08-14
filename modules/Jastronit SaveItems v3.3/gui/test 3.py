import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTextEdit, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt


class FloatingWindow(QMainWindow):
    def __init__(self, content_widget, on_close_callback):
        super().__init__()
        self.setWindowTitle("Plávajúce okno")
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)  # vždy navrchu
        self.resize(300, 200)

        self.content_widget = content_widget
        self.setCentralWidget(self.content_widget)
        self._on_close_callback = on_close_callback

    def closeEvent(self, event):
        """Pri zavretí sa widget vráti do hlavnej appky."""
        if self._on_close_callback:
            self._on_close_callback(self.content_widget)
        event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hlavná aplikácia")
        self.resize(800, 600)

        # Držíme si odpojené widgety, aby ich Python nezmazal
        self._saved_widgets = []

        # Centrálne okno
        self.setCentralWidget(QTextEdit("Hlavné okno"))

        # Dock obsah
        self.dock_content = QTextEdit("Obsah docku")
        self.dock = QDockWidget("Dock panel", self)
        self.dock.setWidget(self.dock_content)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)

        # Nastavenie docku
        self.dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.dock.topLevelChanged.connect(self.on_dock_floated)

        self.floating_window = None

    def on_dock_floated(self, floating):
        """Keď je dock oddokovaný, premeníme ho na samostatné okno."""
        if floating:
            # Vezmeme widget z docku
            content = self.dock.widget()
            self._saved_widgets.append(content)  # udržíme referenciu
            self.dock.setWidget(None)
            self.removeDockWidget(self.dock)

            # Otvoríme ako nové okno
            self.floating_window = FloatingWindow(content, self.re_dock)
            self.floating_window.show()

    def re_dock(self, content_widget):
        """Vrátenie widgetu späť do docku."""
        self.dock.setWidget(content_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()
        self.floating_window = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
