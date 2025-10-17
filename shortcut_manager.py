# shortcut_manager.py
# Widget: Skratky a ich spracovanie cez QtBridge (thread-safe)
# Používa pynput na globálne zachytávanie klávesových skratiek
# Autor: Jastronit
# Verzia: 3.0

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Shortcut Listener + QtBridge pre thread-safe event bus ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- Importy ----////
from PySide6.QtCore import QObject, QMetaObject, Qt, QTimer
from pynput import keyboard
import threading, weakref, time, traceback
# ////-----------------------------------------------------------------------------------------

# ////---- Konštanty ----////
MODIFIERS = ["ctrl", "alt", "shift"]
DEAD_KEYS = {"ˇ", "´", "`", "^", "˚", "¨", "¸", "~"}
INVALID_CHARS = {"?", "_", "ˇ"}
# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- QtBridge - thread-safe event bus pre shortcuty ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- QtBridge ----////
class QtBridge(QObject):
    _instance = None

    # ////---- Inicializácia ----////
    def __init__(self):
        super().__init__()
        self._listeners = {}  # dict: event_name -> [callback1, callback2,...]
    # ////-------------------------------------------------------------------------------------

    # ////---- Singleton inštancia ----////
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    # ////-------------------------------------------------------------------------------------

    # ////---- Eventy ----////
    def on(self, event, callback):
        """Registruje callback pre danú skratku"""
        self._listeners.setdefault(event, []).append(callback)

    def off(self, event, callback):
        """Odregistruje callback"""
        if event in self._listeners:
            self._listeners[event] = [c for c in self._listeners[event] if c != callback]
            if not self._listeners[event]:
                del self._listeners[event]

    def emit(self, event_name, *args, **kwargs):
        if event_name not in self._listeners:
            return

        for cb in list(self._listeners[event_name]):
            try:
                if hasattr(cb, "__self__") and isinstance(cb.__self__, QObject):
                    # Thread-safe volanie v hlavnom GUI threade
                    QTimer.singleShot(0, lambda cb=cb: cb(*args, **kwargs))
                else:
                    # obyčajná funkcia, nie Qt objekt
                    cb(*args, **kwargs)
            except Exception as e:
                print(f"[Bridge] Error calling {cb}: {e}")
    # ////-------------------------------------------------------------------------------------

# ////---- Získanie globálnej inštancie QtBridge ----////
def get_bridge():
    return QtBridge.instance()
# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- ShortcutListener ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- ShortcutListener trieda ----////
class ShortcutListener:
    # ////---- Inicializácia ----////
    def __init__(self):
        print(f"[ShortcutListener] Inicializácia listenera (id: {id(self)})")

        self._objects = []  # weakref objekty
        self._lock = threading.Lock()
        self._pressed_keys = []
        self._last_sent = None
        self._last_event_time = time.time()
        self._stop_event = threading.Event()

        self.bridge = get_bridge()  # použitie QtBridge

        self.listener = self._create_listener()
        self.listener.start()

        threading.Thread(target=self._watchdog_loop, daemon=True).start()
    # ////-------------------------------------------------------------------------------------

    # ////---- Vytváranie listenera a normalizácia kláves ----////
    def _create_listener(self):
        listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        listener.daemon = True
        return listener

    def _normalize_key(self, key):
        try:
            if hasattr(key, 'char') and key.char:
                c = key.char.lower()
                if c in DEAD_KEYS or c in INVALID_CHARS:
                    return None
                return c
            k = str(key).replace('Key.', '').lower()
            if k in ("ctrl_l", "ctrl_r"): return "ctrl"
            if k in ("alt_l", "alt_r"): return "alt"
            if k in ("shift_l", "shift_r"): return "shift"
            return k
        except Exception:
            return None
    # ////-------------------------------------------------------------------------------------

    # ////---- Kompozícia skratky ----////
    def _compose_combo(self):
        if not self._pressed_keys:
            return None
        combo = []
        seen = set()
        for k in self._pressed_keys:
            if k not in seen:
                combo.append(k)
                seen.add(k)
        return "+".join(combo)
    # ////-------------------------------------------------------------------------------------

    # ////---- Registrácia a odregistrácia objektov ----////
    # Poznámka: Toto je staré spracovanie, nahradené QtBridge
    """def register_object(self, obj):
        with self._lock:
            self._objects.append(weakref.ref(obj))

    def unregister_object(self, obj):
        with self._lock:
            self._objects = [ref for ref in self._objects if ref() is not obj]"""
    # ////-------------------------------------------------------------------------------------

    # ////---- Eventy stlačenia a uvoľnenia kláves ----////
    def _on_press(self, key):
        k = self._normalize_key(key)
        if not k or k in self._pressed_keys:
            return

        self._pressed_keys.append(k)
        self._last_event_time = time.time()

        is_fkey = k.startswith("f") and k[1:].isdigit() and 1 <= int(k[1:]) <= 24
        if not any(mod in self._pressed_keys for mod in MODIFIERS) and not is_fkey:
            return

        combo = self._compose_combo()
        if not combo or combo == self._last_sent:
            return
        self._last_sent = combo

        print(f"[ShortcutListener] Shortcut: {combo} (id: {id(self)})")

        # ----- Staré spracovanie registrovaných objektov -----
        """
        with self._lock:
            alive_refs = []
            for ref in self._objects:
                obj = ref()
                if obj is None:
                    continue
                try:
                    if hasattr(obj, "handle_shortcut"):
                        obj.handle_shortcut(combo)
                    alive_refs.append(ref)
                except ReferenceError:
                    continue
                except Exception:
                    traceback.print_exc()
                    alive_refs.append(ref)
            self._objects = alive_refs"""

        # ----- Emit shortcut cez QtBridge (thread-safe pre widgety) -----
        self.bridge.emit(f"shortcut.{combo}")
    # ////-------------------------------------------------------------------------------------

    # ////---- Event uvoľnenia kláves ----////
    def _on_release(self, key):
        k = self._normalize_key(key)
        if not k:
            return
        if k in self._pressed_keys:
            self._pressed_keys.remove(k)
        if self._last_sent and k in self._last_sent.split("+"):
            self._last_sent = None
        self._last_event_time = time.time()
    # ////-------------------------------------------------------------------------------------

    # ////---- Watchdog loop pre reset zaseknutých kláves a reštart listenera ----////
    def _watchdog_loop(self):
        while not self._stop_event.is_set():
            time.sleep(3)
            now = time.time()
            with self._lock:
                self._pressed_keys = [k for k in self._pressed_keys if k not in DEAD_KEYS | INVALID_CHARS]
            if now - self._last_event_time > 10 and self._pressed_keys:
                print("[ShortcutListener] Resetujem zaseknuté klávesy…")
                with self._lock:
                    self._pressed_keys.clear()
                    self._last_sent = None
            if not self.listener.is_alive():
                print("[ShortcutListener] Listener padol, reštartujem…")
                self.listener = self._create_listener()
                self.listener.start()
    # ////-------------------------------------------------------------------------------------

    # ////---- Zastavenie listenera ----////
    def stop(self):
        print("[ShortcutListener] Stop volané")
        self._stop_event.set()

        # Bezpečné zastavenie pynput listenera
        if self.listener:
            try:
                if hasattr(self.listener, "running") and self.listener.running:
                    self.listener.stop()
                # Počkaj chvíľu na ukončenie vlákna
                if hasattr(self.listener, "join"):
                    self.listener.join(timeout=1)
            except Exception as e:
                print(f"[ShortcutListener] Chyba pri stop(): {e}")

        print("[ShortcutListener] Úplne zastavený")
    # ////-------------------------------------------------------------------------------------

# ////----- Singleton inštancia ShortcutListener ----////
_shortcut_listener_instance = None # Toto zaručí, že je len jedna inštancia
# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Funkcie na získanie a zastavenie listenera ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
def get_shortcut_listener():
    global _shortcut_listener_instance
    if _shortcut_listener_instance is None:
        _shortcut_listener_instance = ShortcutListener()
    return _shortcut_listener_instance

def stop_shortcut_listener():
    global _shortcut_listener_instance
    if _shortcut_listener_instance:
        _shortcut_listener_instance.stop()
        _shortcut_listener_instance = None
# ////-----------------------------------------------------------------------------------------
