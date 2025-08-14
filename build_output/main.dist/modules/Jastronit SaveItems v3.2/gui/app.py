# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Importovanie potrebných knižníc ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTextEdit
from PySide6.QtCore import QTimer, Qt
import os

# ////---- Funkcia na nastavenie pozadia widgetu ----////
def set_widget_background(widget, mode="transparent", color=(0, 0, 0), alpha=255):
    """
    Nastaví pozadie widgetu podľa režimu.

    mode:
        "transparent" - úplne priehľadný
        "translucent" - polopriehľadný podľa alpha
        "color"       - plná farba podľa RGB
    color: tuple (R, G, B)
    alpha: 0–255, iba pre translucent
    """

    # Povolí alfa kanál pre widget
    widget.setAttribute(Qt.WA_TranslucentBackground)

    if mode == "transparent":
        widget.setStyleSheet("background: transparent;")
    elif mode == "translucent":
        r, g, b = color
        widget.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, {alpha});")
    elif mode == "color":
        r, g, b = color
        widget.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
# ////-----------------------------------------------------------------------------------------

# ////---- Vytvorenie widgetu pre GUI modul ----////
# Tento widget bude zobrazený v hlavnom okne aplikácie
def get_widget():
    w = QWidget()
    w.setMinimumSize(400, 200)
    w.setMaximumSize(1920, 1080)

    set_widget_background(w, mode="transparent")

    #w.setStyleSheet("background-color: #242424;")
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
    console.setAttribute(Qt.WA_TranslucentBackground, True)
    console.viewport().setAttribute(Qt.WA_TranslucentBackground, True)

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