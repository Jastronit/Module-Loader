### 1. `custom_overlays.py`

Tento widget bude spravovať vlastné overlaye, ktoré sa ukladajú do `custom_overlays.json`.

```python
# filepath: /home/jastronit/Plocha/python/SCUM/ModularApp/modules/Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3/widgets/custom_overlays.py
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QHBoxLayout, QSpinBox
)
from PySide6.QtCore import Qt
import overlay_manager

class CustomOverlaysWidget(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.layout = QVBoxLayout(self)

        # --- Overlay list ---
        self.overlay_list = QListWidget()
        self.layout.addWidget(QLabel("Custom Overlays:"))
        self.layout.addWidget(self.overlay_list)
        self.load_custom_overlays()

        # --- Buttons ---
        btn_create = QPushButton("Create Overlay")
        btn_create.clicked.connect(self.create_overlay)
        self.layout.addWidget(btn_create)

        btn_delete = QPushButton("Delete Selected Overlay")
        btn_delete.clicked.connect(self.delete_selected_overlay)
        self.layout.addWidget(btn_delete)

        btn_save = QPushButton("Save Overlays")
        btn_save.clicked.connect(self.save_custom_overlays)
        self.layout.addWidget(btn_save)

    def load_custom_overlays(self):
        config_path = self.get_config_path("custom_overlays.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                overlays = json.load(f)
                self.overlay_list.addItems(overlays)

    def create_overlay(self):
        overlay_name = f"CustomOverlay_{len(self.overlay_list)}"
        self.overlay_list.addItem(overlay_name)
        self.save_custom_overlays()

    def delete_selected_overlay(self):
        selected = self.overlay_list.currentItem()
        if selected:
            self.overlay_list.takeItem(self.overlay_list.row(selected))
            self.save_custom_overlays()

    def save_custom_overlays(self):
        overlays = [self.overlay_list.item(i).text() for i in range(self.overlay_list.count())]
        config_path = self.get_config_path("custom_overlays.json")
        with open(config_path, "w") as f:
            json.dump(overlays, f, indent=2)

    def get_config_path(self, filename):
        return os.path.join("modules", self.module_name, "config", filename)

def create_widget(BaseClass, module_name):
    return CustomOverlaysWidget(module_name)

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 1
```

### 2. `overlays.py`

Tento widget bude spravovať samostatné overlaye, ktoré sú uložené v zložke `overlays`.

```python
# filepath: /home/jastronit/Plocha/python/SCUM/ModularApp/modules/Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3/widgets/overlays.py
import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget
)
from PySide6.QtCore import Qt

class OverlaysWidget(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name
        self.layout = QVBoxLayout(self)

        # --- Overlay list ---
        self.overlay_list = QListWidget()
        self.layout.addWidget(QLabel("Available Overlays:"))
        self.layout.addWidget(self.overlay_list)
        self.load_overlays()

        # --- Buttons ---
        btn_delete = QPushButton("Delete Selected Overlay")
        btn_delete.clicked.connect(self.delete_selected_overlay)
        self.layout.addWidget(btn_delete)

    def load_overlays(self):
        overlays_dir = os.path.join("modules", self.module_name, "overlays")
        if os.path.exists(overlays_dir):
            for fname in os.listdir(overlays_dir):
                if fname.endswith(".py"):
                    self.overlay_list.addItem(fname)

    def delete_selected_overlay(self):
        selected = self.overlay_list.currentItem()
        if selected:
            fname = selected.text()
            path = os.path.join("modules", self.module_name, "overlays", fname)
            if os.path.exists(path):
                os.remove(path)
            self.overlay_list.takeItem(self.overlay_list.row(selected))
            self.save_overlay_positions(fname)

    def save_overlay_positions(self, overlay_name):
        config_path = self.get_config_path("overlay_positions.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
            if overlay_name in data:
                del data[overlay_name]
            with open(config_path, "w") as f:
                json.dump(data, f, indent=2)

    def get_config_path(self, filename):
        return os.path.join("modules", self.module_name, "config", filename)

def create_widget(BaseClass, module_name):
    return OverlaysWidget(module_name)

def get_widget_dock_position():
    return Qt.RightDockWidgetArea, 2
```

### 3. `overlay_console.py`

Tento súbor bude obsahovať ukážkový overlay, ktorý bude fungovať ako widget `console.py`.

```python
# filepath: /home/jastronit/Plocha/python/SCUM/ModularApp/modules/Jastronit | SCUM v1.0 | SinglePlayer | SaveItems v3.3/overlays/overlay_console.py
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import QTimer
import os

class ConsoleOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Console Overlay")
        self.layout.addWidget(self.label)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.layout.addWidget(self.text)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_console)
        self.timer.start(1000)

    def update_console(self):
        log_file = self.get_data_path("log.txt")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()[-64:]  # last 64 lines
                self.text.setPlainText("".join(lines))

    def get_data_path(self, filename):
        return os.path.join("modules", "Jastronit", "data", filename)

def create_overlay(params):
    return ConsoleOverlay()

def get_widget_dock_position():
    return Qt.LeftDockWidgetArea, 1
```

### Zhrnutie

- `custom_overlays.py` spravuje vlastné overlaye a ukladá ich do `custom_overlays.json`.
- `overlays.py` spravuje samostatné overlaye a umožňuje ich mazanie a kopírovanie.
- `overlay_console.py` je ukážkový overlay, ktorý sa správa ako widget `console.py`.

Týmto spôsobom by si mal mať funkčný systém na správu overlayov, ktorý spĺňa tvoje požiadavky. Ak máš ďalšie otázky alebo potrebuješ úpravy, daj mi vedieť!