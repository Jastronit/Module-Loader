from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QScrollArea, QDockWidget, QPushButton
)
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QPixmap, QDesktopServices, QIcon
import os, sys
import importlib.util

# Cesta k priečinku s modulmi
module_path = "modules"

def load_modules(module_path):
    # Načíta názvy všetkých modulov
    modules = {}
    if not os.path.exists(module_path):
        os.makedirs(module_path)

    for module_name in os.listdir(module_path):
        module_dir = os.path.join(module_path, module_name)
        if os.path.isdir(module_dir):
            # widgets ešte nenačítavame – iba si poznačíme prázdny zoznam
            modules[module_name] = []
    return modules

modules = load_modules(module_path)

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Základný widget pre moduly ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

class BaseWidget(QWidget):
    def __init__(self, module_name=None):
        super().__init__()
        self.module_name = module_name  # meno modulu, do ktorého widget patrí

    # ---- cesty ----
    def get_config_path(self, filename):
        # Vracia absolútnu cestu k súboru v priečinku config
        return os.path.join("modules", self.module_name, "config", filename)

    def get_data_path(self, filename):
        # Vracia absolútnu cestu k súboru v priečinku data
        return os.path.join("modules", self.module_name, "data", filename)

    # ////---- Aktualizácia a zatvorenie widgetu ----////
    def update_widget(self):
        # Volané pri refreshi dát (napr. čítanie configu)
        pass

    def close_widget(self):
        # Volané pri zatvorení widgetu (vypnutie timerov, uloženie stavu)
        pass


# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Hlavné okno GUI aplikácie ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(1500, 800) # Nastavenie veľkosti okna fixne pre problém s widgetmi
        self.setWindowTitle("Jastronit | Module Loader v0.1 beta")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)

        # Ľavý panel s obrázkom a zoznamom modulov
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5,5,5,5) #

        # Obrázok
        self.image_label = QLabel()
        pixmap = QPixmap(480, 320)
        pixmap.fill(Qt.lightGray)
        self.image_label.setPixmap(pixmap)
        self.image_label.setFixedSize(480, 320)
        left_layout.addWidget(self.image_label)

        # ---- Načítanie obrázka modulu ----
        img_path = os.path.join("assets", "pictures", "480x320.png")
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.image_label.setPixmap(pixmap.scaled(480, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Scroll zoznam modulov
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.list_widget = QListWidget()
        self.list_widget.addItems(modules.keys())
        scroll_area.setWidget(self.list_widget)
        scroll_area.setFixedWidth(480)

        left_layout.addWidget(scroll_area)
        main_layout.addWidget(left_panel)

        # ---- Jednoduché textové odkazy ----
        discord_link = QLabel('<a href="https://discord.gg/cqg6dDj5pW">💬 Discord: Join our community and get more modules!</a>')
        discord_link.setOpenExternalLinks(True)

        coffee_link = QLabel('<a href="https://buymeacoffee.com/jastronit">☕ Buy me a coffee: And support my work</a>')
        coffee_link.setOpenExternalLinks(True)

        # pridanie do ľavého panelu pod zoznam modulov
        left_layout.addWidget(discord_link)
        left_layout.addWidget(coffee_link)

        # Pravá dock oblasť pre widgety
        self.right_dock = RightDockArea(image_label=self.image_label)
        main_layout.addWidget(self.right_dock)

        # Pripojenie výberu modulu
        self.list_widget.currentTextChanged.connect(self.right_dock.load_widgets)

class RightDockArea(QMainWindow):
    # Pravá dock oblasť správa widgety ako klasický QMainWindow
    def __init__(self, image_label):
        super().__init__()
        self.setFixedWidth(1000)
        self.setContentsMargins(0,0,0,0)
        self.setDockNestingEnabled(True)

        self.image_label = image_label  # uložíme si QLabel z ľavej strany

    def load_widgets(self, module_name):
        # ---- Načítanie obrázka modulu ----
        img_path = os.path.join(module_path, module_name, "assets", "pictures", "480x320.png")
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.image_label.setPixmap(pixmap.scaled(480, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # fallback – šedé pozadie
            pixmap = QPixmap(480, 320)
            pixmap.fill(Qt.lightGray)
            self.image_label.setPixmap(pixmap)

        # Odstráni existujúce dock widgety
        for dock in self.findChildren(QDockWidget):
            self.removeDockWidget(dock)
            dock.setParent(None)

        module_dir = os.path.join(module_path, module_name, "widgets")
        if not os.path.exists(module_dir):
            return print(f"Modul {module_name} nemá žiadne widgety.")

        # Načíta všetky .py súbory v priečinku widgets
        for fname in os.listdir(module_dir):
            if fname.endswith(".py"):
                file_path = os.path.join(module_dir, fname)
                widget_name = os.path.splitext(fname)[0]

                # načítanie .py súboru ako modul
                spec = importlib.util.spec_from_file_location(widget_name, file_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[widget_name] = mod
                spec.loader.exec_module(mod)

                # vytvorenie widgetu – očakávame triedu odvodenú z BaseWidget
                widget = None
                if hasattr(mod, "create_widget"):
                    widget = mod.create_widget(BaseWidget, module_name)
                elif hasattr(mod, "Widget"):  # alternatíva: priamo trieda
                    widget = mod.Widget(module_name)

                if widget is None:
                    continue

                dock = QDockWidget(widget_name, self)
                dock.setAllowedAreas(Qt.AllDockWidgetAreas)
                dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
                dock.setWidget(widget)

                # Default dock pozícia
                area = Qt.RightDockWidgetArea
                if hasattr(mod, "get_widget_dock_position"):
                    try:
                        area = mod.get_widget_dock_position()
                    except Exception as e:
                        print(f"Chyba pri získaní pozície widgetu {widget_name}: {e}")

                self.addDockWidget(area, dock)

# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Hlavná funkcia pre spustenie GUI aplikácie s callbackom na vypnutie main.py----////
# /////////////////////////////////////////////////////////////////////////////////////////////
def main(on_close_callback=None):
    app = QApplication(sys.argv)

    # Vytvorenie hlavného okna aplikácie
    window = MainApp()

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