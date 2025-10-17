# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Overlay Manager Imports ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

import os
import sys
import json
import importlib.util
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from shortcut_manager import get_bridge

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Overlay window class ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
class OverlayWindow(QWidget):
    def __init__(self, widget, name, params, manager, module_name):
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.manager = manager
        self.name = name
        self.module_name = module_name
        self.params = params
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(name)
        self.setGeometry(params.get("x", 100), params.get("y", 100), params.get("w", 400), params.get("h", 200))
        self.setStyleSheet(f"background-color: {params.get('bg', 'rgba(0,0,0,0)')}; border: none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(widget)
        self.edit_mode = False
        self.drag_pos = None
        self.resizing = False
        self.overlay_visible = True
        self.user_visible = params.get("user_visible", True) # user_visible parameter

        # Label pre edit mode
        self.edit_label = QLabel("EDIT MODE ACTIVE")
        self.edit_label.setStyleSheet("color: yellow; font-size: 18px; background: rgba(0,0,0,120);")
        self.edit_label.setAlignment(Qt.AlignCenter)
        self.edit_label.hide()
        layout.addWidget(self.edit_label)

    # ////---- Funkcia na zobrazenie/skrytie overlay ----////
    def set_overlay_visible(self, show: bool):
        """self.overlay_visible = show
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setVisible(show)"""
        effective = show and self.user_visible
        self.overlay_visible = effective
        self.setVisible(effective)
    # ////-------------------------------------------------------------------------------------

    # ////---- Funkcia pre režim úprav ----////
    def set_edit_mode(self, state):
        self.edit_mode = state
        self.hide()  # Skryť okno pred zmenou flagov (dôležité pre Windows aj Linux)
        self.edit_label.setVisible(state) # Zobraziť/Skryť edit label
        self.setWindowFlag(Qt.WindowTransparentForInput, not state) # Ak nie je v edit režime, ignoruj vstupy
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True) # Nastaví okno vždy navrchu
        # self.edit_label.setVisible(state) # Zobraziť/Skryť edit label EDIT: prehodené vyššie robilo to problémy
        self.show()  # Znova zobraziť okno po zmene flagov
    # ////-------------------------------------------------------------------------------------

    # ////---- Funkcia pre kliknutie a presun ----////
    def mousePressEvent(self, event):
        if self.edit_mode and event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        if self.edit_mode and event.button() == Qt.RightButton:
            self.resizing = True
            self.resize_start = event.globalPosition().toPoint()
            self.start_geom = self.geometry()
    # ////-------------------------------------------------------------------------------------

    # ////---- Funkcia pre presun a zmenu veľkosti ----////
    def mouseMoveEvent(self, event):
        if self.edit_mode and self.drag_pos:
            new_pos = event.globalPosition().toPoint() - self.drag_pos
            self.move(new_pos)
            self.manager.save_overlay_positions()
        if self.edit_mode and self.resizing:
            delta = event.globalPosition().toPoint() - self.resize_start
            new_w = max(100, self.start_geom.width() + delta.x())
            new_h = max(50, self.start_geom.height() + delta.y())
            self.resize(new_w, new_h)
            self.manager.save_overlay_positions()
    # ////-------------------------------------------------------------------------------------

    # ////---- Funkcia pre ukončenie presunu/zmeny veľkosti ----////
    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.resizing = False
    # ////-------------------------------------------------------------------------------------

    # ////---- Funkcia pre klávesové skratky ----////
    def keyPressEvent(self, event):
        if self.edit_mode and event.key() == Qt.Key_Delete:
            self.manager.remove_overlay(self.name)
    # ////-------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Overlay Manager Class ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
class OverlayManager:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.overlays = {}  # Meno -> OverlayWindow
        self.global_show = True
        self.edit_mode = False

        # ---- QtBridge signály ----
        self.bridge = get_bridge()
        self.bridge.on("shortcut.f9", self.toggle_global_show)
        self.bridge.on("shortcut.f10", self.toggle_edit_mode)

        # ---- Centrálny label pre edit režim ---- EDIT: Plánovaná prerábka
        """self.edit_label = QLabel("EDIT MODE ACTIVE")
        self.edit_label.setStyleSheet("color: yellow; font-size: 24px; background: rgba(0,0,0,150);")
        self.edit_label.setAlignment(Qt.AlignCenter)
        self.edit_label.setWindowFlag(Qt.FramelessWindowHint)
        self.edit_label.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.edit_label.setAttribute(Qt.WA_TranslucentBackground)
        self.edit_label.resize(200, 50)
        self.edit_label.hide()"""

        self.load_all_overlays()
        # self.stop_event = None # nie je momentálne používané

    # ////---- Načíta všetky overlaye z každého modulu ----////
    def load_all_overlays(self, modules_dir="modules"):
        for module_name in os.listdir(modules_dir):
            overlays_dir = os.path.join(modules_dir, module_name, "overlays")
            if not os.path.isdir(overlays_dir):
                continue
            # Pre každý .py súbor v overlays zložke
            for fname in os.listdir(overlays_dir):
                if fname.endswith(".py"):
                    file_path = os.path.join(overlays_dir, fname)
                    overlay_name = f"{module_name}:{fname}"

                    # Default hodnoty
                    default_params = {"x":100,"y":100,"w":400,"h":200,"bg":"rgba(0,0,0,0)"}
                    # Načítaj uložené pozície (prepíšu defaulty)
                    params = self.load_overlay_position(module_name, fname, default_params)
                    # Načítaj widget z overlay súboru
                    widget = self.load_overlay_widget(file_path, module_name, params)
                    if widget:
                        self.add_overlay(widget, overlay_name, params, module_name)
    # ////-------------------------------------------------------------------------------------

    # ////---- Načíta overlay widget z daného súboru ----////
    def load_overlay_widget(self, file_path, module_name, params):
        spec = importlib.util.spec_from_file_location("overlay", file_path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            if hasattr(mod, "create_overlay"):
                return mod.create_overlay(params)   # <-- tu už posielam celé params
        except Exception as e:
            print(f"Chyba pri načítaní overlay {file_path}: {e}")
        return None
    # ////-------------------------------------------------------------------------------------

    # ////---- Uloží aktuálny overlay ako vlastný ----////
    def add_overlay(self, widget, name, params, module_name):
        win = OverlayWindow(widget, name, params, self, module_name)
        win.show() if self.global_show else win.hide()
        self.overlays[name] = win
    # ////-------------------------------------------------------------------------------------

    # ////---- Odstráni overlay podľa mena ----////
    def remove_overlay(self, name):
        if name in self.overlays:
            self.overlays[name].close()
            del self.overlays[name]
            self.save_overlay_positions()
    # ////-------------------------------------------------------------------------------------

    # ////---- Nastaví globálne zobrazenie všetkých overlayov ----////
    def set_global_show(self, show: bool):
        print(f"[OverlayManager] set_global_show({show})")
        self.global_show = show
        for win in self.overlays.values():
            win.set_overlay_visible(show)
    # ////-------------------------------------------------------------------------------------

    # ////---- Nastaví režim úprav pre všetky overlaye ----////
    """def set_edit_mode(self, state):
        print(f"[OverlayManager] set_edit_mode({state})")
        self.edit_mode = state
        for win in self.overlays.values():
            win.set_edit_mode(state)
            # netreba opakovane volať setWindowFlag tu, už to robí OverlayWindow
            # len nastav viditeľnosť podľa režimu
            effective = self.global_show and win.user_visible
            win.setVisible(effective or state)"""
    
    def set_edit_mode(self, state):
        print(f"[OverlayManager] set_edit_mode({state})")
        self.edit_mode = state
    
        # ---- Zmena viditeľnosti centrálneho labelu ----
        if state:
            self.edit_label.show()
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            self.edit_label.move(
                (screen_geometry.width() - self.edit_label.width()) // 2,
                (screen_geometry.height() - self.edit_label.height()) // 2
            )
        else:
            self.edit_label.hide()

        # ---- Prepnutie všetkých overlayov do edit režimu (len ak potrebné) ----
        for win in self.overlays.values():
            # Overlay okno sa nemení, widget spracuje svoj vlastný edit režim
            pass
    # ////-------------------------------------------------------------------------------------

    # ////---- Funkcia pre spracovanie skratiek ----//// EDIT: Teraz cez QtBridge
    """def handle_shortcut(self, key: str):
        # Táto funkcia je volaná ShortcutListenerom pri každej stlačenej klávese!
        key = key.lower()
        if key == "f9":
            self.toggle_global_show()
        elif key == "f10":
            self.toggle_edit_mode()"""
    # ////-------------------------------------------------------------------------------------

    # ////---- Prepne globálne zobrazenie všetkých overlayov ----////
    def toggle_global_show(self):
        print("[OverlayManager] toggle_global_show() called")
        self.global_show = not self.global_show
        for win in self.overlays.values():
            win.set_overlay_visible(self.global_show)
    # ////-------------------------------------------------------------------------------------

    # ////---- Prepne režim úprav pre všetky overlaye ----////
    def toggle_edit_mode(self):
        print("[OverlayManager] toggle_edit_mode() called")
        self.edit_mode = not self.edit_mode
        for win in self.overlays.values():
            win.set_edit_mode(self.edit_mode)
            effective = self.global_show and win.user_visible
            win.setVisible(effective or self.edit_mode)
    # ////-------------------------------------------------------------------------------------

    # ////---- Uloží pozície všetkých overlayov do súborov ----////
    def save_overlay_positions(self):
        positions_by_module = {}
        custom_positions_by_module = {}

        for name, win in self.overlays.items():
            geo = win.geometry()
            new_params = {
                "x": geo.x(), "y": geo.y(),
                "w": geo.width(), "h": geo.height(),
                "bg": win.params.get("bg", "rgba(0,0,0,0)"),
                "user_visible": win.user_visible
            }

            if ":" in name:
                module, overlay = name.split(":", 1)

                # ---- klasické overlaye (overlay.py súbory) ----
                if overlay.endswith(".py"):
                    if module not in positions_by_module:
                        positions_by_module[module] = {}
                    positions_by_module[module][overlay] = new_params

                # ---- custom overlays (custom_overlays.json) ----
                else:
                    if module not in custom_positions_by_module:
                        custom_positions_by_module[module] = {}
                    custom_positions_by_module[module][overlay] = new_params

        # Ulož klasické overlaye
        for module, overlays in positions_by_module.items():
            config_dir = os.path.join("modules", module, "config")
            os.makedirs(config_dir, exist_ok=True)
            path = os.path.join(config_dir, "python_overlays.json")
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        old_data = json.load(f)
                else:
                    old_data = {}
            except Exception:
                old_data = {}
            old_data.update(overlays)
            with open(path, "w") as f:
                json.dump(old_data, f, indent=2)

        # Ulož custom overlays
        for module, overlays in custom_positions_by_module.items():
            config_dir = os.path.join("modules", module, "config")
            os.makedirs(config_dir, exist_ok=True)
            path = os.path.join(config_dir, "custom_overlays.json")
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        old_data = json.load(f)
                else:
                    old_data = {}
            except Exception:
                old_data = {}

            # update existujúcich custom overlays
            for overlay_name, params in overlays.items():
                if overlay_name in old_data:
                    old_data[overlay_name].update(params)

            with open(path, "w") as f:
                json.dump(old_data, f, indent=2)

    # ////-------------------------------------------------------------------------------------

    # ////---- Načíta pozíciu overlayu z konfiguračného súboru ----////
    def load_overlay_position(self, module, overlay, default_params):
        path = os.path.join("modules", module, "config", "python_overlays.json")
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    if overlay in data:
                        return data[overlay]
            except Exception:
                pass
        return default_params
      
    # ////---- Stop overlay managera ----////
    def stop(self):
        for win in list(self.overlays.values()):
            try:
                win.close()
            except Exception:
                pass
        self.save_overlay_positions()
        self.overlays.clear()
        # self.stop_event = True # nie je momentálne používané
    # ////-------------------------------------------------------------------------------------

_manager_instance = None

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Štart a stop Overlay Managera ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

def start_overlay_manager():
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = OverlayManager()
    return _manager_instance

def stop_overlay_manager():
    global _manager_instance
    if _manager_instance:
        _manager_instance.stop()
        _manager_instance = None
