# modules/<tvoj_module>/overlays/test_overlay.py
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

def create_overlay(params):
    """
    Vytvorenie testovacieho overlay widgetu.
    params: dict s x, y, w, h, bg, user_visible
    """
    w = QWidget()
    layout = QVBoxLayout(w)
    label = QLabel("Testovací Overlay\n(Zmena veľkosti a show/hide test)")
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)

    # voliteľne: nastavíme pozadie podľa params
    w.setStyleSheet(f"background-color: {params.get('bg', 'rgba(0,0,0,127)')}; border: 1px solid yellow;")

    # widget sa prispôsobí veľkosti, ale manager nastaví okno podľa params
    return w

