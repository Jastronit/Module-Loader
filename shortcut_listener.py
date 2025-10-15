# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Detekcia skratiek s modifikátormi ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
from pynput import keyboard
import threading, weakref, time, traceback

MODIFIERS = ["ctrl", "alt", "shift"]
DEAD_KEYS = {"ˇ", "´", "`", "^", "˚", "¨", "¸", "~"}
INVALID_CHARS = {"?", "_", "ˇ"}

class ShortcutListener:
    def __init__(self):
        print(f"[ShortcutListener] Inicializácia listenera (id: {id(self)})")
        self._objects = []                     # weakref objekty
        self._lock = threading.Lock()
        self._pressed_keys = []                # list pre zachovanie poradia
        self._last_sent = None
        self._last_event_time = time.time()

        self._stop_event = threading.Event()  # pre bezpečný shutdown

        self.listener = self._create_listener()
        self.listener.start()

        # Samoobnovovací kontrolný thread
        threading.Thread(target=self._watchdog_loop, daemon=True).start()

    # /////////////////////////////////////////////////////////////////////////////////////////
    # ////---- Helpery ----////
    # /////////////////////////////////////////////////////////////////////////////////////////

    def _create_listener(self):
        listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        listener.daemon = True
        return listener

    def _normalize_key(self, key):
        """Normalizuje názvy kláves a odstráni mŕtve/invalid znaky."""
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

    def _compose_combo(self):
        """Zachová presné poradie kláves, bez duplicít."""
        if not self._pressed_keys:
            return None
        combo = []
        seen = set()
        for k in self._pressed_keys:
            if k not in seen:
                combo.append(k)
                seen.add(k)
        return "+".join(combo)

    # /////////////////////////////////////////////////////////////////////////////////////////
    # ////---- Registrácia objektov ----////
    # /////////////////////////////////////////////////////////////////////////////////////////

    def register_object(self, obj):
        with self._lock:
            self._objects.append(weakref.ref(obj))

    def unregister_object(self, obj):
        with self._lock:
            self._objects = [ref for ref in self._objects if ref() is not obj]

    # /////////////////////////////////////////////////////////////////////////////////////////
    # ////---- Eventy z pynput ----////
    # /////////////////////////////////////////////////////////////////////////////////////////

    def _on_press(self, key):
        k = self._normalize_key(key)
        if not k or k in self._pressed_keys:
            return

        self._pressed_keys.append(k)
        self._last_event_time = time.time()

        # Výnimka: F-klávesy (F1-F24) môžu ísť aj bez modifikátora
        is_fkey = k.startswith("f") and k[1:].isdigit() and 1 <= int(k[1:]) <= 24

        # Počkaj, kým nebude aspoň jeden modifikátor
        if not any(mod in self._pressed_keys for mod in MODIFIERS) and not is_fkey:
            return

        combo = self._compose_combo()
        if not combo or combo == self._last_sent:
            return
        self._last_sent = combo

        print(f"[ShortcutListener] Detekovaná skratka: {combo} (id: {id(self)})")

        with self._lock:
            alive_refs = []
            for ref in self._objects:
                obj = ref()
                if obj is None:
                    continue
                try:
                    obj.handle_shortcut(combo)
                    alive_refs.append(ref)
                except ReferenceError:
                    continue
                except Exception:
                    traceback.print_exc()
                    alive_refs.append(ref)
            self._objects = alive_refs

    def _on_release(self, key):
        k = self._normalize_key(key)
        if not k:
            return
        if k in self._pressed_keys:
            self._pressed_keys.remove(k)
        if self._last_sent and k in self._last_sent.split("+"):
            self._last_sent = None
        self._last_event_time = time.time()

    # /////////////////////////////////////////////////////////////////////////////////////////
    # ////---- Watchdog - sleduje funkčnosť listenera ----////
    # /////////////////////////////////////////////////////////////////////////////////////////

    def _watchdog_loop(self):
        # Ak listener prestane reagovať, automaticky ho reštartuje.
        # Kontrola stop eventu pre bezpečný shutdown
        while not self._stop_event.is_set():
            time.sleep(3)
            now = time.time()
            # Odstráni neplatné/mŕtve klávesy
            with self._lock:
                self._pressed_keys = [k for k in self._pressed_keys if k not in DEAD_KEYS | INVALID_CHARS]

            # Ak sa 10 sekúnd nič nestalo → reset pressed_keys (zaseknutý kláves)
            if now - self._last_event_time > 10 and self._pressed_keys:
                print("[ShortcutListener] Resetujem zaseknuté klávesy…")
                with self._lock:
                    self._pressed_keys.clear()
                    self._last_sent = None

            # Ak by sa listener ukončil, znovu ho spustí
            if not self.listener.is_alive():
                print("[ShortcutListener] Listener padol, reštartujem…")
                self.listener = self._create_listener()
                self.listener.start()

    # Nová funkcia na bezpečný shutdown
    def stop(self):
        print("[ShortcutListener] Stop volané")
        self._stop_event.set()
        if self.listener and self.listener.running:
            self.listener.stop()
        # dať malú pauzu, nech sa watchdog thread ukončí
        time.sleep(0.1)

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Globálna inštancia ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

_shortcut_listener_instance = None

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