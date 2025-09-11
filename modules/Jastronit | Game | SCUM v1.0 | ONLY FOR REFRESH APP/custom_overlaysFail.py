import os
import json
import importlib.util
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel, QListWidget,
    QHBoxLayout, QSpinBox, QMessageBox, QApplication, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette
import overlay_manager

# ---- Detekcia dark mode ----
def is_dark_mode():
    palette = QApplication.instance().palette()
    window_color = palette.color(QPalette.Window)
    return window_color.lightness() < 128

# ---- JSON CONFIG ----
def get_config_path(module_name):
    return os.path.join("modules", module_name, "config", "custom_overlays.json")

def get_default_overlay_params():
    return {
        "x": 100, "y": 100, "w": 400, "h": 200,
        "bg": "rgba(0,0,0,127)",
        "widgets": [],
        "widget_bgs": {},
        "user_visible": True
    }

def load_custom_overlays(module_name):
    path = get_config_path(module_name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_custom_overlays(module_name, data):
    path = get_config_path(module_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---- DYNAMIC WIDGET IMPORT ----
def load_widget(widget_name, BaseClass, module_name):
    widget_path = os.path.join("modules", module_name, "widgets", f"{widget_name}.py")
    if not os.path.exists(widget_path):
        print(f"Widget {widget_name} pre modul {module_name} neexistuje.")
        return None
    try:
        spec = importlib.util.spec_from_file_location(widget_name, widget_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        w = mod.create_widget(BaseClass, module_name)
        if not isinstance(w, QWidget):
            print(f"Widget {widget_name} nevrátil QWidget!")
            return None
        return w
    except Exception as e:
        print(f"Chyba pri načítaní widgetu {widget_name}: {e}")
        return None

def build_overlay_window(data, BaseClass, module_name, name):
    if not data.get("widgets"):
        return  # prázdny overlay, nič nezobrazuj
    overlay_widget = QWidget()
    vbox = QVBoxLayout(overlay_widget)
    overlay_widget.setStyleSheet(f"background-color: {data.get('bg', 'rgba(0,0,0,127)')}; border: none;")

    for widget_name in data.get("widgets", []):
        w = load_widget(widget_name, BaseClass, module_name)
        if w:
            bg = data.get("widget_bgs", {}).get(widget_name, "rgba(0,0,0,0)")
            w.setStyleSheet(f"background-color: {bg}; border: none;")
            vbox.addWidget(w)

    mgr = overlay_manager.start_overlay_manager()
    mgr.add_overlay(
        overlay_widget,
        name=f"{module_name}:{name}",
        params={
            "x": data.get("x", 100),
            "y": data.get("y", 100),
            "w": data.get("w", 400),
            "h": data.get("h", 200),
            "bg": data.get("bg", "rgba(0,0,0,127)"),
            "module_name": module_name
        },
        module_name=module_name
    )
    # nastav viditeľnosť podľa user_visible a globálneho toggle
    win = mgr.overlays[f"{module_name}:{name}"]
    win.user_visible = data.get("user_visible", True)
    win.set_overlay_visible(win.user_visible and mgr.global_show)

# ---- CUSTOM OVERLAYS WIDGET ----
def create_widget(BaseClass, module_name):
    class CustomOverlaysWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            self.setWindowTitle("Vlastné Overlays")
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            # banner
            banner_file = "CUSTOM_OVERLAY_DARK.png" if is_dark_mode() else "CUSTOM_OVERLAY.png"
            banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners", banner_file)
            if os.path.exists(banner_path):
                self.banner = QLabel()
                pixmap = QPixmap(banner_path)
                self.banner.setPixmap(pixmap.scaledToHeight(32, Qt.SmoothTransformation))
                self.banner.setAlignment(Qt.AlignCenter)
                layout.addWidget(self.banner)

            # zoznam overlayov
            layout.addWidget(QLabel("Zoznam vlastných overlays:"))
            self.overlay_list = QListWidget()
            layout.addWidget(self.overlay_list)
            self.overlay_list.itemSelectionChanged.connect(self.on_select_overlay)

            # checkboxy widgetov
            layout.addWidget(QLabel("Vytvoriť overlay z widgetov:"))
            self.chk_prisoner = QCheckBox("Prisoner")
            self.chk_console = QCheckBox("Console")
            layout.addWidget(self.chk_prisoner)
            layout.addWidget(self.chk_console)

            # nastavenie farieb widgetov
            self.widget_bg_spins = {}
            for wname in ["prisoner","console"]:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(f"Pozadie {wname}:"))
                spins = []
                for color in ["R","G","B","A"]:
                    spin = QSpinBox(); spin.setRange(0,255); spin.setValue(127 if color=="A" else 0)
                    hbox.addWidget(QLabel(color+":")); hbox.addWidget(spin)
                    spins.append(spin)
                layout.addLayout(hbox)
                self.widget_bg_spins[wname] = spins

            # overlay background
            color_layout = QHBoxLayout()
            layout.addWidget(QLabel("Pozadie overlayu:"))
            self.spin_r = QSpinBox(); self.spin_g = QSpinBox(); self.spin_b = QSpinBox(); self.spin_a = QSpinBox()
            for spin,val,label in zip([self.spin_r,self.spin_g,self.spin_b,self.spin_a],[0,0,0,127],["R","G","B","A"]):
                spin.setRange(0,255); spin.setValue(val); color_layout.addWidget(QLabel(label+":")); color_layout.addWidget(spin)
                spin.valueChanged.connect(self.update_color_preview)
            layout.addLayout(color_layout)
            self.color_preview = QLabel(); self.color_preview.setFixedHeight(24); layout.addWidget(self.color_preview)
            self.update_color_preview()

            # ovládacie tlačidlá
            btn_create = QPushButton("Vytvoriť nový overlay"); btn_create.clicked.connect(self.create_overlay); layout.addWidget(btn_create)
            btn_delete = QPushButton("Vymazať vybraný overlay"); btn_delete.clicked.connect(self.delete_selected_overlay); layout.addWidget(btn_delete)
            btn_toggle = QPushButton("Toggle visibility"); btn_toggle.clicked.connect(self.toggle_selected_overlay); layout.addWidget(btn_toggle)

            self.selected_overlay = None
            self.custom_overlays = load_custom_overlays(module_name)
            self.refresh_overlay_list()

            # načítaj všetky overlaye
            for name, data in self.custom_overlays.items():
                build_overlay_window(data, BaseClass, module_name, name)

        # --- helpers ---
        def update_color_preview(self):
            r,g,b,a = self.spin_r.value(), self.spin_g.value(), self.spin_b.value(), self.spin_a.value()
            self.color_preview.setStyleSheet(f"background-color: rgba({r},{g},{b},{a}); border:1px solid #888;")
        def get_overlay_bg(self): return f"rgba({self.spin_r.value()},{self.spin_g.value()},{self.spin_b.value()},{self.spin_a.value()})"
        def get_widget_bg(self, name): return f"rgba({','.join(str(s.value()) for s in self.widget_bg_spins[name])})"

        def refresh_overlay_list(self):
            self.overlay_list.clear()
            mgr = overlay_manager.start_overlay_manager()
            for cname, params in self.custom_overlays.items():
                full_name = f"{module_name}:{cname}"
                item_text = cname + (" ✅" if params.get("user_visible", True) else " ❌")
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, cname)
                self.overlay_list.addItem(item)

        def on_select_overlay(self):
            items = self.overlay_list.selectedItems()
            self.selected_overlay = items[0].data(Qt.UserRole) if items else None

        def toggle_selected_overlay(self):
            if not self.selected_overlay: return
            fname = self.selected_overlay
            full_name = f"{module_name}:{fname}"
            mgr = overlay_manager.start_overlay_manager()
            data = self.custom_overlays[fname]
            new_state = not data.get("user_visible", True)
            data["user_visible"] = new_state
            # update overlay window
            if full_name in mgr.overlays:
                win = mgr.overlays[full_name]
                win.user_visible = new_state
                win.set_overlay_visible(new_state and mgr.global_show)
            save_custom_overlays(module_name, self.custom_overlays)
            self.refresh_overlay_list()

        def create_overlay(self):
            base_name, idx = "Overlay", 1
            while f"{base_name}_{idx}" in self.custom_overlays: idx+=1
            name = f"{base_name}_{idx}"
            widgets=[]
            if self.chk_prisoner.isChecked(): widgets.append("prisoner")
            if self.chk_console.isChecked(): widgets.append("console")
            if not widgets: QMessageBox.warning(self,"Chyba","Vyber aspoň jeden widget!"); return
            params = get_default_overlay_params()
            params["widgets"]=widgets; params["bg"]=self.get_overlay_bg()
            for w in widgets: params["widget_bgs"][w]=self.get_widget_bg(w)
            self.custom_overlays[name]=params
            save_custom_overlays(module_name,self.custom_overlays)
            self.refresh_overlay_list()
            build_overlay_window(params,BaseClass,module_name,name)

        def delete_selected_overlay(self):
            if not self.selected_overlay: return
            del self.custom_overlays[self.selected_overlay]
            save_custom_overlays(module_name,self.custom_overlays)
            self.refresh_overlay_list()

        def show_selected_overlay(self):
            if not self.selected_overlay: return
            build_overlay_window(self.custom_overlays[self.selected_overlay],BaseClass,module_name,self.selected_overlay)

    return CustomOverlaysWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1
