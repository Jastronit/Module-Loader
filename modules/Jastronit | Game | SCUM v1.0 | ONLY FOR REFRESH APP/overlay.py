import sys, os
import importlib.util
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QPushButton, QLabel, QComboBox, QSlider,
    QListWidget, QHBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt
import overlay_manager

def import_widget(module_name):
    module_path = os.path.join(os.path.dirname(__file__), f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def list_overlays(module_name):
    overlays_dir = os.path.join("modules", module_name, "overlays")
    return [f for f in os.listdir(overlays_dir) if f.endswith(".py")] if os.path.isdir(overlays_dir) else []

def create_widget(BaseClass, module_name):
    class OverlayDockWidget(BaseClass):
        def __init__(self):
            super().__init__(module_name)
            layout = QVBoxLayout(self)
            self.setLayout(layout)

            # --- Overlay zoznam ---
            layout.addWidget(QLabel("List all overlays:"))
            self.overlay_list = QListWidget()
            layout.addWidget(self.overlay_list)
            self.refresh_overlay_list()

            # --- Elementy ---
            layout.addWidget(QLabel("Vytvoriť overlay z widgetu:"))
            self.chk_prisoner = QCheckBox("Prisoner")
            self.chk_console = QCheckBox("Console")
            layout.addWidget(self.chk_prisoner)
            layout.addWidget(self.chk_console)

            # --- Pozadie pre elementy ---
            self.element_bg = {}
            for name in ["prisoner", "console"]:
                el_layout = QHBoxLayout()
                el_layout.addWidget(QLabel(f"Background {name}:"))
                spin_r = QSpinBox(); spin_r.setRange(0,255); spin_r.setValue(0)
                spin_g = QSpinBox(); spin_g.setRange(0,255); spin_g.setValue(0)
                spin_b = QSpinBox(); spin_b.setRange(0,255); spin_b.setValue(0)
                spin_a = QSpinBox(); spin_a.setRange(0,255); spin_a.setValue(0)
                el_layout.addWidget(QLabel("R:")); el_layout.addWidget(spin_r)
                el_layout.addWidget(QLabel("G:")); el_layout.addWidget(spin_g)
                el_layout.addWidget(QLabel("B:")); el_layout.addWidget(spin_b)
                el_layout.addWidget(QLabel("A:")); el_layout.addWidget(spin_a)
                layout.addLayout(el_layout)
                self.element_bg[name] = (spin_r, spin_g, spin_b, spin_a)

            # --- Overlay pozadie ---
            color_layout = QHBoxLayout()
            layout.addWidget(QLabel("Background:"))
            self.spin_r = QSpinBox(); self.spin_r.setRange(0,255); self.spin_r.setValue(0)
            self.spin_g = QSpinBox(); self.spin_g.setRange(0,255); self.spin_g.setValue(0)
            self.spin_b = QSpinBox(); self.spin_b.setRange(0,255); self.spin_b.setValue(0)
            self.spin_a = QSpinBox(); self.spin_a.setRange(0,255); self.spin_a.setValue(127)
            color_layout.addWidget(QLabel("R:")); color_layout.addWidget(self.spin_r)
            color_layout.addWidget(QLabel("G:")); color_layout.addWidget(self.spin_g)
            color_layout.addWidget(QLabel("B:")); color_layout.addWidget(self.spin_b)
            color_layout.addWidget(QLabel("A:")); color_layout.addWidget(self.spin_a)
            layout.addLayout(color_layout)
            self.color_preview = QLabel()
            self.color_preview.setFixedHeight(24)
            layout.addWidget(self.color_preview)
            self.update_color_preview()
            for spin in [self.spin_r, self.spin_g, self.spin_b, self.spin_a]:
                spin.valueChanged.connect(self.update_color_preview)

            btn_create = QPushButton("Create Overlay")
            btn_create.clicked.connect(self.create_overlay_from_widget)
            layout.addWidget(btn_create)

            btn_copy = QPushButton("Copy widget to overlays")
            btn_copy.clicked.connect(self.copy_widget_to_overlays)
            layout.addWidget(btn_copy)

            btn_save = QPushButton("Save Overlay")
            btn_save.clicked.connect(self.save_custom_overlay)
            layout.addWidget(btn_save)

            btn_delete = QPushButton("Delete Overlay")
            btn_delete.clicked.connect(self.delete_selected_overlay)
            layout.addWidget(btn_delete)

            btn_showhide = QPushButton("Show/Hide selected Overlay")
            btn_showhide.clicked.connect(self.toggle_selected_overlay)
            layout.addWidget(btn_showhide)

            self.selected_widget = None

        def refresh_overlay_list(self):
            self.overlay_list.clear()
            for fname in list_overlays(module_name):
                self.overlay_list.addItem(fname)

        def update_color_preview(self):
            r = self.spin_r.value()
            g = self.spin_g.value()
            b = self.spin_b.value()
            a = self.spin_a.value()
            self.color_preview.setStyleSheet(f"background-color: rgba({r},{g},{b},{a}); border: 1px solid #888;")

        def get_overlay_bg(self):
            r = self.spin_r.value()
            g = self.spin_g.value()
            b = self.spin_b.value()
            a = self.spin_a.value()
            return f"rgba({r},{g},{b},{a})"

        def get_element_bg(self, name):
            spins = self.element_bg[name]
            r = spins[0].value()
            g = spins[1].value()
            b = spins[2].value()
            a = spins[3].value()
            return f"rgba({r},{g},{b},{a})"

        def create_overlay_from_widget(self):
            overlay_widget = QWidget()
            vbox = QVBoxLayout(overlay_widget)
            overlay_widget.setStyleSheet(f"background-color: {self.get_overlay_bg()}; border: none;")
            if self.chk_prisoner.isChecked():
                prisoner_mod = self.import_widget("prisoner")
                prisoner_widget = prisoner_mod.create_widget(BaseClass, module_name)
                prisoner_widget.setStyleSheet(f"background-color: {self.get_element_bg('prisoner')}; border: none;")
                vbox.addWidget(prisoner_widget)
            if self.chk_console.isChecked():
                console_mod = self.import_widget("console")
                console_widget = console_mod.create_widget(BaseClass, module_name)
                console_widget.setStyleSheet(f"background-color: {self.get_element_bg('console')}; border: none;")
                vbox.addWidget(console_widget)
            overlay_manager.start_overlay_manager().add_overlay(
                overlay_widget,
                name=f"CustomOverlay_{module_name}_{os.urandom(4).hex()}",
                params={
                    "x": 400,
                    "y": 200,
                    "w": 400,
                    "h": 300,
                    "bg": self.get_overlay_bg(),
                    "module_name": module_name
                },
                module_name=module_name
            )

        def copy_widget_to_overlays(self):
            # Skopíruje vybraný widget do overlays/ ako overlay.py
            src = os.path.join("modules", module_name, "widgets", "prisoner.py")
            dst_dir = os.path.join("modules", module_name, "overlays")
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, "overlay_prisoner.py")
            import shutil
            shutil.copy(src, dst)
            self.refresh_overlay_list()

        def import_widget(self, widget_name):
            widget_path = os.path.join("modules", module_name, "widgets", f"{widget_name}.py")
            spec = importlib.util.spec_from_file_location(widget_name, widget_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod

        def save_custom_overlay(self):
            selected = self.overlay_list.currentItem()
            if selected:
                fname = selected.text()
                src_path = os.path.join("modules", module_name, "overlays", fname)
                if os.path.exists(src_path):
                    with open(src_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Upravíme background na nový
                    new_bg = self.get_overlay_bg()
                    lines = content.splitlines()
                    for i, line in enumerate(lines):
                        if line.strip().startswith("self.setStyleSheet("):
                            lines[i] = f'        self.setStyleSheet("background-color: {new_bg}; border: none;")'
                            break
                    new_content = "\n".join(lines)
                    with open(src_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Overlay {fname} updated with new background {new_bg}.")
                else:
                    print(f"Overlay file {fname} does not exist.")
            else:
                print("No overlay selected to save.")

        def delete_selected_overlay(self):
            selected = self.overlay_list.currentItem()
            if selected:
                fname = selected.text()
                path = os.path.join("modules", module_name, "overlays", fname)
                if os.path.exists(path):
                    os.remove(path)
                overlay_manager.start_overlay_manager().remove_overlay(f"{module_name}:{fname}")
                self.refresh_overlay_list()

        def toggle_selected_overlay(self):
            selected = self.overlay_list.currentItem()
            if selected:
                fname = selected.text()
                name = f"{module_name}:{fname}"
                mgr = overlay_manager.start_overlay_manager()
                win = mgr.overlays.get(name)
                if win:
                    win.set_overlay_visible(not win.overlay_visible)
                    # Pri hide môžeš vypnúť timer v overlay widgete, ak existuje
                    if hasattr(win, "timer") and not win.overlay_visible:
                        win.timer.stop()

    return OverlayDockWidget()

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1

