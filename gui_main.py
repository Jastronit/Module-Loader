# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Importovanie potrebných knižníc ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
import os
import sys
import importlib.util
import configparser
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget, QPushButton, QHBoxLayout, QLabel, QColorDialog
from PySide6.QtGui import QColor, QPalette

MODULES_DIR = "modules"

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Funkcie na načítanie a spustenie gui modulov ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- Náčítanie GUI aplikácie z modulu ----////
def find_gui_app(module_path):
    gui_app_path = os.path.join(module_path, "gui", "app.py")
    return gui_app_path if os.path.isfile(gui_app_path) else None
# ////-----------------------------------------------------------------------------------------

# ////---- Vlastný titulok pre dock widget ----////
def create_custom_titlebar(dock, widget, reload_func, module_path):
    titlebar = QWidget()
    layout = QHBoxLayout(titlebar)
    layout.setContentsMargins(2, 0, 2, 0)

    label = QLabel(dock.windowTitle())
    btn_settings = QPushButton("⚙")
    btn_settings.setFixedSize(20, 20)

    def open_settings():
        color = QColorDialog.getColor(options=QColorDialog.ShowAlphaChannel)
        if color.isValid():
            r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
            config_path = os.path.join(module_path, "gui", "config.ini")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            config = configparser.ConfigParser()
            config.read(config_path)
            if "Background" not in config:
                config["Background"] = {}
            config["Background"]["mode"] = "translucent" if a < 255 else "color"
            config["Background"]["color"] = f"{r},{g},{b}"
            config["Background"]["alpha"] = str(a)
            with open(config_path, "w", encoding="utf-8") as f:
                config.write(f)
            reload_func(widget, dock)

    btn_settings.clicked.connect(open_settings)

    layout.addWidget(label)
    layout.addStretch()
    layout.addWidget(btn_settings)
    titlebar.setLayout(layout)

    dock.setTitleBarWidget(titlebar)
# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Hlavné okno aplikácie ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jastronit | Module Loader v1.0.0")
        self.resize(400, 600) # nastaví veľkosť okna
        self.setMinimumSize(400, 200)  # <-- minimálna veľkosť okna

        self.setStyleSheet("background-color: #242424;")
        self.setDockOptions(QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks)
        self.load_all_modules()

    # ////---- Načítanie a pridanie všetkých GUI modulov do docku ----////
    def load_all_modules(self):
        all_modules = [os.path.join(MODULES_DIR, d) for d in os.listdir(MODULES_DIR) if os.path.isdir(os.path.join(MODULES_DIR, d))]
        for module_path in all_modules:
            gui_app_path = find_gui_app(module_path)
            if gui_app_path:

                # Načítanie modulu priamo tu, aby sme mali prístup k funkciám aj widgetu
                spec = importlib.util.spec_from_file_location("gui_app", gui_app_path)
                gui_app = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(gui_app)
                except Exception as e:
                    print(f"Chyba pri načítaní {gui_app_path}: {e}")
                    continue

                # Získanie widgetu z modulu
                if hasattr(gui_app, "get_widget"):
                    widget = gui_app.get_widget()
                else:
                    print(f"{gui_app_path}: Chýba funkcia get_widget()")
                    widget = QWidget()

                dock = QDockWidget(os.path.basename(module_path), self)
                dock.setWidget(widget)

                # Pripojenie funkcie reload_background po oddokovaní
                if hasattr(gui_app, "reload_widget_background"):
                    gui_app.reload_widget_background(widget, dock)

                create_custom_titlebar(dock, widget, gui_app.reload_widget_background, module_path)

                #dock.setAttribute(Qt.WA_TranslucentBackground, True)  # Nastavenie docku ako priehľadného
                dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

                # Zisti oblasť z modulu, inak defaultne vpravo
                area = Qt.RightDockWidgetArea  # Defaultná oblasť
                if hasattr(gui_app, "get_dock_area"):
                    area = gui_app.get_dock_area()
                self.addDockWidget(area, dock)
            else:
                print(f"Modul {module_path} nemá GUI appku.")

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Hlavná funkcia pre spustenie GUI aplikácie ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
def main(on_close_callback=None):
    app = QApplication(sys.argv)

    # Vytvorenie hlavného okna aplikácie
    window = MainWindow()

    def handle_close(event):
        if on_close_callback:
            try:
                on_close_callback()
            except Exception as e:
                print(f"Chyba pri volaní on_close_callback: {e}")
        event.accept()
    
    window.closeEvent = handle_close  # Priradenie vlastnej funkcie na zatvorenie okna
    window.show()
    sys.exit(app.exec())

# ////---- Volanie hlavnej funkcie ----////
if __name__ == "__main__":
    main()
