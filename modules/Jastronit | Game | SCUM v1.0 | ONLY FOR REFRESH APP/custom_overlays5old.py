# custom_overlays3.py
import os
import json
import importlib.util
import glob
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QSpinBox, QMessageBox, QApplication, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette
import overlay_manager

# ////////////////// DraggableListWidget //////////////////
class DraggableListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QListWidget.InternalMove)

# //// Dark mode check ////
def is_dark_mode():
    palette = QApplication.instance().palette()
    return palette.color(QPalette.Window).lightness() < 128

# ---------------- JSON CONFIG ----------------
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

# ---------------- DYNAMIC WIDGET IMPORT ----------------
def load_widget(widget_name, BaseClass, module_name):
    widget_path = os.path.join("modules", module_name, "widgets", f"{widget_name}.py")
    if not os.path.exists(widget_path):
        print(f"Widget {widget_name} for module {module_name} does not exist.")
        return None
    spec = importlib.util.spec_from_file_location(widget_name, widget_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "create_widget"):
        return mod.create_widget(BaseClass, module_name)
    return None

def build_overlay_window(name, params, BaseClass, module_name):
    overlay_widget = QWidget()
    vbox = QVBoxLayout(overlay_widget)
    overlay_widget.setStyleSheet(f"background-color: {params.get('bg','rgba(0,0,0,127)')}; border: none;")
    for widget_name in params.get("widgets", []):
        w = load_widget(widget_name, BaseClass, module_name)
        if w:
            bg = params.get("widget_bgs", {}).get(widget_name, "rgba(0,0,0,0)")
            try: w.setStyleSheet(f"background-color: {bg}; border: none;")
            except Exception: pass
            vbox.addWidget(w)
    mgr = overlay_manager.start_overlay_manager()
    full_name = f"{module_name}:{name}"
    mgr.add_overlay(
        overlay_widget,
        name=full_name,
        params={
            "x": params.get("x",100), "y": params.get("y",100),
            "w": params.get("w",400), "h": params.get("h",200),
            "bg": params.get("bg","rgba(0,0,0,127)"),
            "module_name": module_name
        },
        module_name=module_name
    )
    win = mgr.overlays.get(full_name)
    if win:
        win.user_visible = params.get("user_visible", True)
        win.set_overlay_visible(win.user_visible and mgr.global_show)

# ---------------- MAIN WIDGET ----------------
def create_widget(BaseClass, module_name):
    class CustomOverlaysWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            self.setWindowTitle("Vlastné Overlays (drag & drop)")
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            # banner
            try:
                banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners/CUSTOM_OVERLAY.png")
                if is_dark_mode(): banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners/CUSTOM_OVERLAY_DARK.png")
                if os.path.exists(banner_path):
                    self.banner = QLabel()
                    pixmap = QPixmap(banner_path)
                    self.banner.setPixmap(pixmap.scaledToHeight(32, Qt.SmoothTransformation))
                    self.banner.setAlignment(Qt.AlignCenter)
                    layout.addWidget(self.banner)
            except Exception: pass

            layout.addWidget(QLabel("Zoznam vlastných overlays:"))
            self.overlay_list = QListWidget()
            layout.addWidget(self.overlay_list)
            self.overlay_list.itemSelectionChanged.connect(self.on_select_overlay)

            layout.addWidget(QLabel("Vyber widgety (ťahaj pre poradie, zaškrtni pre zahrnutie):"))
            self.widget_list = DraggableListWidget()
            self.widget_list.setSelectionMode(QListWidget.SingleSelection)
            layout.addWidget(self.widget_list)

            # widgets background controls
            self.widget_bg_spins = {}
            widgets_path = os.path.join("modules", module_name, "widgets")
            files = sorted(glob.glob(os.path.join(widgets_path, "*.py"))) if os.path.isdir(widgets_path) else []
            for file in files:
                wname = os.path.splitext(os.path.basename(file))[0]
                if wname.startswith("custom_overlays") or wname=="__init__": continue
                item = QListWidgetItem(wname)
                flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled
                item.setFlags(flags)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, wname)
                self.widget_list.addItem(item)
                # bg controls
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(f"Pozadie {wname}:"))
                spins = []
                for color in ["R","G","B","A"]:
                    spin = QSpinBox(); spin.setRange(0,255)
                    spin.setValue(0 if color!="A" else 127)
                    hbox.addWidget(QLabel(color+":")); hbox.addWidget(spin)
                    spins.append(spin)
                layout.addLayout(hbox)
                self.widget_bg_spins[wname] = spins

            # overlay bg controls
            color_layout = QHBoxLayout()
            layout.addWidget(QLabel("Pozadie overlayu:"))
            self.spin_r = QSpinBox(); self.spin_r.setRange(0,255); self.spin_r.setValue(0)
            self.spin_g = QSpinBox(); self.spin_g.setRange(0,255); self.spin_g.setValue(0)
            self.spin_b = QSpinBox(); self.spin_b.setRange(0,255); self.spin_b.setValue(0)
            self.spin_a = QSpinBox(); self.spin_a.setRange(0,255); self.spin_a.setValue(127)
            for label, spin in zip(["R","G","B","A"], [self.spin_r, self.spin_g, self.spin_b, self.spin_a]):
                color_layout.addWidget(QLabel(label+":")); color_layout.addWidget(spin)
            layout.addLayout(color_layout)

            # buttons
            btn_create = QPushButton("Vytvoriť nový overlay"); btn_create.clicked.connect(self.create_overlay)
            btn_delete = QPushButton("Vymazať vybraný overlay"); btn_delete.clicked.connect(self.delete_selected_overlay)
            btn_toggle = QPushButton("Toggle visibility (selected)"); btn_toggle.clicked.connect(self.toggle_selected_overlay)
            btn_rename = QPushButton("Premenovať overlay"); btn_rename.clicked.connect(self.rename_selected_overlay)
            for btn in [btn_create, btn_delete, btn_toggle, btn_rename]: layout.addWidget(btn)

            self.selected_overlay = None
            self.custom_overlays = load_custom_overlays(module_name)
            self.refresh_overlay_list()
            for cname, params in self.custom_overlays.items():
                build_overlay_window(cname, params, BaseClass, module_name)

        # --- helpers ---
        def get_overlay_bg(self):
            r,g,b,a = self.spin_r.value(), self.spin_g.value(), self.spin_b.value(), self.spin_a.value()
            return f"rgba({r},{g},{b},{a})"

        def get_widget_bg(self, widget_name):
            spins = self.widget_bg_spins.get(widget_name)
            if not spins: return "rgba(0,0,0,0)"
            r,g,b,a = [s.value() for s in spins]
            return f"rgba({r},{g},{b},{a})"

        def refresh_widget_list_from_json(self, cname):
            if not cname:
                for i in range(self.widget_list.count()): self.widget_list.item(i).setCheckState(Qt.Unchecked)
                return
            params = self.custom_overlays.get(cname, {})
            wanted = params.get("widgets", [])
            widget_bgs = params.get("widget_bgs", {})
            for i in range(self.widget_list.count()):
                it = self.widget_list.item(i); wname = it.data(Qt.UserRole)
                it.setCheckState(Qt.Checked if wname in wanted else Qt.Unchecked)
                if wname in widget_bgs:
                    try:
                        inside = widget_bgs[wname].split("(")[1].split(")")[0]
                        parts = [int(x.strip()) for x in inside.split(",")]
                        spins = self.widget_bg_spins.get(wname)
                        if spins and len(parts)==4:
                            for s,v in zip(spins, parts): s.setValue(v)
                    except Exception: pass

        def refresh_overlay_list(self):
            self.overlay_list.clear()
            mgr = overlay_manager.start_overlay_manager()
            self.custom_overlays = load_custom_overlays(module_name)
            for cname, params in self.custom_overlays.items():
                name = f"{module_name}:{cname}"
                if name in mgr.overlays: win = mgr.overlays[name]; state_icon="✅ " if getattr(win,'user_visible',True) else "❌ "
                else: state_icon="✅ " if params.get("user_visible",True) else "❌ "
                item = QListWidgetItem(state_icon + cname); item.setData(Qt.UserRole, cname)
                self.overlay_list.addItem(item)

        def create_overlay(self):
            base_name, idx = "Overlay", 1
            while f"{base_name}_{idx}" in self.custom_overlays: idx+=1
            name=f"{base_name}_{idx}"
            widgets=[self.widget_list.item(i).data(Qt.UserRole) for i in range(self.widget_list.count()) if self.widget_list.item(i).checkState()==Qt.Checked]
            if not widgets: QMessageBox.warning(self,"Chyba","Vyber aspoň jeden widget!"); return
            params = get_default_overlay_params(); params["widgets"]=widgets; params["bg"]=self.get_overlay_bg(); params["widget_bgs"]={w:self.get_widget_bg(w) for w in widgets}; params["user_visible"]=True
            self.custom_overlays[name]=params
            save_custom_overlays(module_name, self.custom_overlays)
            self.refresh_overlay_list()
            build_overlay_window(name, params, BaseClass, module_name)

        def on_select_overlay(self):
            items=self.overlay_list.selectedItems()
            self.selected_overlay = items[0].data(Qt.UserRole) if items else None
            self.refresh_widget_list_from_json(self.selected_overlay)

        def delete_selected_overlay(self):
            if not self.selected_overlay: return
            if self.selected_overlay in self.custom_overlays: del self.custom_overlays[self.selected_overlay]; save_custom_overlays(module_name, self.custom_overlays)
            mgr=overlay_manager.start_overlay_manager()
            full_name=f"{module_name}:{self.selected_overlay}"
            if full_name in mgr.overlays: mgr.remove_overlay(full_name)
            self.refresh_overlay_list()

        def toggle_selected_overlay(self):
            items=self.overlay_list.selectedItems()
            if not items: return
            cname=items[0].data(Qt.UserRole)
            mgr=overlay_manager.start_overlay_manager()
            full_name=f"{module_name}:{cname}"
            if full_name in mgr.overlays:
                win=mgr.overlays[full_name]
                new_state=not getattr(win,'user_visible',True)
                win.user_visible=new_state
                win.set_overlay_visible(new_state and mgr.global_show)
            self.custom_overlays=load_custom_overlays(module_name)
            if cname in self.custom_overlays: self.custom_overlays[cname]['user_visible']=not self.custom_overlays[cname].get('user_visible',True); save_custom_overlays(module_name, self.custom_overlays)
            self.refresh_overlay_list()

        def rename_selected_overlay(self):
            if not self.selected_overlay: return
            old_name = self.selected_overlay
            new_name, ok = QInputDialog.getText(self, "Premenovať overlay", "Nový názov:", text=old_name)
            if ok and new_name and new_name!=old_name:
                self.custom_overlays[new_name]=self.custom_overlays.pop(old_name)
                save_custom_overlays(module_name, self.custom_overlays)
                mgr=overlay_manager.start_overlay_manager()
                full_old=f"{module_name}:{old_name}"
                if full_old in mgr.overlays:
                    win=mgr.overlays.pop(full_old)
                    full_new=f"{module_name}:{new_name}"
                    mgr.overlays[full_new]=win
                self.refresh_overlay_list()

    return CustomOverlaysWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1

