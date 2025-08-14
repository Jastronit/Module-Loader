# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Importovanie potrebných knižníc ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
import os
import sys
import importlib.util
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget, QWidget

MODULES_DIR = "modules"

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Funkcie na načítanie a spustenie gui modulov ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- Náčítanie GUI aplikácie z modulu ----////
def find_gui_app(module_path):
    gui_app_path = os.path.join(module_path, "gui", "app.py")
    return gui_app_path if os.path.isfile(gui_app_path) else None
# ////-----------------------------------------------------------------------------------------

# ////---- Načítanie widgetu z GUI aplikácie ----////
def load_gui_widget(gui_app_path):
    spec = importlib.util.spec_from_file_location("gui_app", gui_app_path)
    gui_app = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(gui_app)
        if hasattr(gui_app, "get_widget"):
            return gui_app.get_widget()
        else:
            print(f"{gui_app_path}: Chýba funkcia get_widget()")
    except Exception as e:
        print(f"Chyba pri načítaní {gui_app_path}: {e}")
    return QWidget()  # prázdny widget ak zlyhá načítanie

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Hlavné okno aplikácie ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jastronit Mod Loader")
        self.resize(520, 800) # nastaví veľkosť okna
        self.setMinimumSize(480, 270)  # <-- minimálna veľkosť okna

        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        #self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #242424;")
        self.setDockOptions(QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks)
        self.load_all_modules()

    # ////---- Načítanie a pridanie všetkých GUI modulov do docku ----////
    def load_all_modules(self):
        all_modules = [os.path.join(MODULES_DIR, d) for d in os.listdir(MODULES_DIR) if os.path.isdir(os.path.join(MODULES_DIR, d))]
        for module_path in all_modules:
            gui_app_path = find_gui_app(module_path)
            if gui_app_path:
                widget = load_gui_widget(gui_app_path)

                # Nastav priehľadnosť widgetu
                #widget.setAttribute(Qt.WA_TranslucentBackground, True)
                #widget.setStyleSheet("background: translucent;")

                dock = QDockWidget(os.path.basename(module_path), self)
                dock.setWidget(widget)

                if hasattr(gui_app, "reload_background"):
                    dock.topLevelChanged.connect(lambda floating: gui_app.reload_background(widget))

                # Nastav priehľadnosť docku
                dock.setAttribute(Qt.WA_TranslucentBackground, True)
                dock.setStyleSheet("background: transparent; border: none;")

                # Nastav priehľadnosť docku
                #dock.setAttribute(Qt.WA_TranslucentBackground, True)
                #dock.setStyleSheet("background: transparent; border: none;")

                dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

                # Zisti oblasť z modulu, inak defaultne vpravo
                spec = importlib.util.spec_from_file_location("gui_app", gui_app_path)
                gui_app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(gui_app)
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