import os
import json
import glob
import importlib.util
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel, QListWidget,
    QHBoxLayout, QSpinBox, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPalette
import overlay_manager

def is_dark_mode():
    palette = QApplication.instance().palette()
    window_color = palette.color(QPalette.Window)
    return window_color.lightness() < 128

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

def load_widget(widget_name, BaseClass, module_name):
    widget_path = os.path.join("modules", module_name, "widgets", f"{widget_name}.py")
    if not os.path.exists(widget_path):
        return None
    spec = importlib.util.spec_from_file_location(widget_name, widget_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.create_widget(BaseClass, module_name)

def build_overlay_window(data, BaseClass, module_name, name):
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

def create_widget(BaseClass, module_name):
    class CustomOverlaysWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            self.setWindowTitle("Vlastné Overlays")
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            # banner
            if is_dark_mode():
                banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners/CUSTOM_OVERLAY.png")
            else:
                banner_path = os.path.join(os.path.dirname(__file__), "../assets/banners/CUSTOM_OVERLAY_DARK.png")
            if os.path.exists(banner_path):
                banner = QLabel()
                pixmap = QPixmap(banner_path)
                banner.setAlignment(Qt.AlignCenter)
                banner.setPixmap(pixmap.scaledToHeight(32, Qt.SmoothTransformation))
                layout.addWidget(banner)

            layout.addWidget(QLabel("Zoznam vlastných overlays:"))
            self.overlay_list = QListWidget()
            layout.addWidget(self.overlay_list)
            self.overlay_list.itemSelectionChanged.connect(self.on_select_overlay)

            # dynamické widgety
            layout.addWidget(QLabel("Vytvoriť overlay z widgetov:"))
            self.widget_checkboxes = {}
            self.widget_bg_spins = {}
            widgets_path = os.path.join("modules", module_name, "widgets")
            for file in glob.glob(os.path.join(widgets_path, "*.py")):
                wname = os.path.splitext(os.path.basename(file))[0]
                if wname in ["__init__", "custom_overlays", "custom_overlays2"]:
                    continue
                chk = QCheckBox(wname)
                layout.addWidget(chk)
                self.widget_checkboxes[wname] = chk
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(f"Pozadie {wname}:"))
                spins = []
                for c in ["R","G","B","A"]:
                    s = QSpinBox(); s.setRange(0,255); s.setValue(0 if c!="A" else 127)
                    hbox.addWidget(QLabel(c+":")); hbox.addWidget(s); spins.append(s)
                layout.addLayout(hbox)
                self.widget_bg_spins[wname] = spins

            # pozadie overlayu
            color_layout = QHBoxLayout()
            layout.addWidget(QLabel("Pozadie overlayu:"))
            self.spin_r=QSpinBox(); self.spin_g=QSpinBox(); self.spin_b=QSpinBox(); self.spin_a=QSpinBox()
            for s in [self.spin_r,self.spin_g,self.spin_b,self.spin_a]: s.setRange(0,255)
            self.spin_a.setValue(127)
            for lbl,spin in zip(["R","G","B","A"],[self.spin_r,self.spin_g,self.spin_b,self.spin_a]):
                color_layout.addWidget(QLabel(lbl+":")); color_layout.addWidget(spin); spin.valueChanged.connect(self.update_color_preview)
            layout.addLayout(color_layout)
            self.color_preview=QLabel(); self.color_preview.setFixedHeight(24); layout.addWidget(self.color_preview)
            self.update_color_preview()

            # buttons
            b1=QPushButton("Vytvoriť nový overlay"); b1.clicked.connect(self.create_overlay); layout.addWidget(b1)
            b2=QPushButton("Vymazať vybraný overlay"); b2.clicked.connect(self.delete_selected_overlay); layout.addWidget(b2)
            b3=QPushButton("Toggle visibility"); b3.clicked.connect(self.toggle_selected_overlay); layout.addWidget(b3)

            self.selected_overlay=None
            self.custom_overlays=load_custom_overlays(module_name)
            self.refresh_overlay_list()
            for name,data in self.custom_overlays.items():
                build_overlay_window(data,BaseClass,module_name,name)

        def toggle_selected_overlay(self):
            sel=self.overlay_list.currentItem()
            if not sel: return
            raw=sel.text().strip(); fname=raw[2:].strip() if raw.startswith(("✅","❌")) else raw
            full=f"{module_name}:{fname}"
            mgr=overlay_manager.start_overlay_manager()
            if full in mgr.overlays:
                win=mgr.overlays[full]; new_state=not getattr(win,"user_visible",True)
                win.user_visible=new_state; win.set_overlay_visible(new_state and mgr.global_show)
                cfg=get_config_path(module_name)
                if os.path.exists(cfg):
                    with open(cfg,"r",encoding="utf-8") as f: data=json.load(f)
                    if fname in data: data[fname]["user_visible"]=new_state
                    with open(cfg,"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
            self.refresh_overlay_list()

        def update_color_preview(self):
            r,g,b,a=self.spin_r.value(),self.spin_g.value(),self.spin_b.value(),self.spin_a.value()
            self.color_preview.setStyleSheet(f"background-color: rgba({r},{g},{b},{a}); border: 1px solid #888;")

        def get_overlay_bg(self):
            r,g,b,a=self.spin_r.value(),self.spin_g.value(),self.spin_b.value(),self.spin_a.value()
            return f"rgba({r},{g},{b},{a})"

        def get_widget_bg(self,w):
            r,g,b,a=[s.value() for s in self.widget_bg_spins[w]]
            return f"rgba({r},{g},{b},{a})"

        def refresh_overlay_list(self):
            self.overlay_list.clear()
            mgr=overlay_manager.start_overlay_manager()
            cfg=get_config_path(module_name)
            if not os.path.exists(cfg): return
            with open(cfg,"r") as f: data=json.load(f)
            for cname,params in data.items():
                name=f"{module_name}:{cname}"
                if name in mgr.overlays: visible=getattr(mgr.overlays[name],"user_visible",True)
                else: visible=params.get("user_visible",True)
                prefix="✅ " if visible else "❌ "
                self.overlay_list.addItem(prefix+cname)

        def create_overlay(self):
            base,idx="Overlay",1
            while f"{base}_{idx}" in self.custom_overlays: idx+=1
            name=f"{base}_{idx}"
            widgets=[w for w,c in self.widget_checkboxes.items() if c.isChecked()]
            if not widgets: QMessageBox.warning(self,"Chyba","Vyber aspoň jeden widget!"); return
            params=get_default_overlay_params(); params["widgets"]=widgets; params["bg"]=self.get_overlay_bg()
            for w in widgets: params["widget_bgs"][w]=self.get_widget_bg(w)
            self.custom_overlays[name]=params
            save_custom_overlays(module_name,self.custom_overlays)
            self.refresh_overlay_list()
            build_overlay_window(params,BaseClass,module_name,name)

        def on_select_overlay(self):
            items=self.overlay_list.selectedItems()
            self.selected_overlay=items[0].text() if items else None

        def delete_selected_overlay(self):
            if not self.selected_overlay: return
            raw=self.selected_overlay.strip(); fname=raw[2:].strip() if raw.startswith(("✅","❌")) else raw
            if fname in self.custom_overlays:
                del self.custom_overlays[fname]; save_custom_overlays(module_name,self.custom_overlays)
            mgr=overlay_manager.start_overlay_manager(); full=f"{module_name}:{fname}"
            if full in mgr.overlays: mgr.remove_overlay(full)
            self.refresh_overlay_list()

    return CustomOverlaysWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea,1

