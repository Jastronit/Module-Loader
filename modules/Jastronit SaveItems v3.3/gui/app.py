# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Importovanie potrebných knižníc ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPalette
import os
import configparser
# ////-----------------------------------------------------------------------------------------

# ////---- Funkcia na nastavenie pozadia widgetu ----////
def set_widget_background(widget, mode="color", color=(0, 0, 0), alpha=255):
    # Nastavenie pozadia widgetu podľa zvoleného režimu
    if mode == "color":
        widget.setAttribute(Qt.WA_TranslucentBackground, False)
        r, g, b = color
        widget.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
    elif mode == "translucent":
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        r, g, b = color
        widget.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, {alpha});")
# ////-----------------------------------------------------------------------------------------

def apply_translucent_background(widget, color: QColor):
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        p = widget.palette()
        p.setColor(QPalette.Base, color)
        widget.setPalette(p)
        widget.setAutoFillBackground(True)
        print(f"[DEBUG] Nastavená farba: {color.getRgb()}")

# ////---- Funkcia na opätovné načítanie pozadia widgetu ----////
def reload_widget_background(widget, dock=None):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), "config.ini")
    config.read(config_path)

    # Načítanie farby a priehľadnosti z configu
    bg_color_str = config.get("Background", "color", fallback="0,0,0")
    bg_alpha = config.getint("Background", "alpha", fallback=255)
    bg_color = tuple(map(int, bg_color_str.split(',')))
    r, g, b = bg_color

    if bg_alpha < 255:
        
        # Priehľadné pozadie
        widget.setAttribute(Qt.WA_TranslucentBackground, True)
        dock.setAutoFillBackground(True)
        apply_translucent_background(widget, QColor(r, g, b, bg_alpha))
        #widget.setAutoFillBackground(True)

        # Ak je dock prítomný, tiež nastav jeho widget na priehľadný
        if dock:            
            dock.setAttribute(Qt.WA_TranslucentBackground, True)
            dock.setAutoFillBackground(True)
            apply_translucent_background(widget, QColor(r, g, b, bg_alpha))
            #dock.setAutoFillBackground(True)
            #dock.setStyleSheet("QDockWidget::title { background-color: transparent; }")
            #dock.widget().setAttribute(Qt.WA_TranslucentBackground, True)
            #dock.widget().setAutoFillBackground(True)
        
        #widget.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, {bg_alpha});")
        #widget.apply_translucent_background(widget.dock, QColor({r}, {g}, {b}, {bg_alpha}))
    else:
        # Plnofarebné pozadie
        widget.setAttribute(Qt.WA_TranslucentBackground, False)
        widget.setAutoFillBackground(True)

        if dock:
            dock.setAttribute(Qt.WA_TranslucentBackground, False)
            dock.setAutoFillBackground(True)
            dock.setStyleSheet(f"QDockWidget::title {{ background-color: rgb({r}, {g}, {b}); }}")
            dock.widget().setAttribute(Qt.WA_TranslucentBackground, False)
            dock.widget().setAutoFillBackground(True)

        widget.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")

# ////-----------------------------------------------------------------------------------------

# ////---- Vytvorenie widgetu pre Mod Loader ----////
# Tento widget bude zobrazený v hlavnom okne aplikácie
def get_widget():
    w = QWidget()

    # Nastavenie veľkosti widgetu
    w.setMinimumSize(400, 200)
    w.setMaximumSize(1920, 1080)

    # Načítanie pozadia z configu
    reload_widget_background(w)

    layout = QVBoxLayout(w)

    # Textové pole pre zobrazenie logu
    console = QTextEdit()
    console.setReadOnly(True)

    console.setStyleSheet("""
        background-color: rgba(0, 0, 0, 0);
        color: white;
        border: none;
    """)
    console.setFrameStyle(0)
    #console.setAttribute(Qt.WA_TranslucentBackground, True)
    #console.viewport().setAttribute(Qt.WA_TranslucentBackground, True)

    layout.addWidget(console)

    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "log.txt"))

    # ////---- Aktualizácia konzoly ----////
    def update_console():
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                console.setPlainText(f.read())
        else:
            console.setPlainText("Log nenájdený.")
        # Posuňeme scrollbar na úplný spodok
        scrollbar = console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ////---- Nastavenie časovača pre aktualizáciu konzoly ----////
    timer = QTimer(w)
    timer.timeout.connect(update_console)
    timer.start(1000)  # každú sekundu
    update_console()

    return w

# ////---- Získanie oblasti docku pre widget ----////
# Vráti oblasť, do ktorej sa má widget pridať (napr. Left, Right, Top, Bottom)
def get_dock_area():
    return Qt.LeftDockWidgetArea  # Pridá widget do ľavej oblasti docku