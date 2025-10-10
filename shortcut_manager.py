import weakref
from pynput import keyboard
import threading

class ShortcutManager:
    def __init__(self):
        # shortcut_str -> set of (weakref callback, weakref owner, scope)
        self.shortcut_callbacks = {}
        self._pressed_keys = set()
        self._already_triggered = set()
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()
        self._lock = threading.Lock()

    def register_shortcut(self, shortcut, callback, owner=None, scope="global"):
        # Start listener if not already running
        if not self.listener.running:
            self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self.listener.start()
        # Register a shortcut callback with optional owner and scope ('global', 'module', 'overlay').
        with self._lock:
            if shortcut not in self.shortcut_callbacks:
                self.shortcut_callbacks[shortcut] = set()
            wr_cb = weakref.WeakMethod(callback) if hasattr(callback, "__self__") else weakref.ref(callback)
            wr_owner = weakref.ref(owner) if owner is not None else None
            self.shortcut_callbacks[shortcut].add((wr_cb, wr_owner, scope))

    def unregister_shortcut(self, shortcut, callback=None, scope=None):
        # Unregister one or all callbacks for a shortcut.
        with self._lock:
            if shortcut not in self.shortcut_callbacks:
                return
            to_remove = set()
            for cb, owner_ref, s in self.shortcut_callbacks[shortcut]:
                if scope and s != scope:
                    continue
                real_cb = cb() if isinstance(cb, (weakref.WeakMethod, weakref.ref)) else cb
                if callback is None or real_cb == callback:
                    to_remove.add((cb, owner_ref, s))
            self.shortcut_callbacks[shortcut].difference_update(to_remove)
            if not self.shortcut_callbacks[shortcut]:
                del self.shortcut_callbacks[shortcut]

    def unregister_scope(self, scope_name):
        # Unregister all shortcuts in a given scope (e.g., on module unload).
        with self._lock:
            for shortcut in list(self.shortcut_callbacks.keys()):
                filtered = {(cb, ow, s) for cb, ow, s in self.shortcut_callbacks[shortcut] if s != scope_name}
                if filtered:
                    self.shortcut_callbacks[shortcut] = filtered
                else:
                    del self.shortcut_callbacks[shortcut]

    def cleanup(self):
        # Remove dead weakrefs.
        with self._lock:
            to_delete = []
            for shortcut, cbs in self.shortcut_callbacks.items():
                alive = set()
                for cb, owner_ref, scope in cbs:
                    real_cb = cb() if isinstance(cb, (weakref.WeakMethod, weakref.ref)) else cb
                    real_owner = owner_ref() if owner_ref else None
                    if real_cb and (owner_ref is None or real_owner):
                        alive.add((cb, owner_ref, scope))
                if alive:
                    self.shortcut_callbacks[shortcut] = alive
                else:
                    to_delete.append(shortcut)
            for shortcut in to_delete:
                del self.shortcut_callbacks[shortcut]

    def _normalize_key(self, k):
        if isinstance(k, keyboard.Key):
            if k in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                return "ctrl"
            if k in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                return "alt"
            if k in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                return "shift"
            return str(k).replace("Key.", "")
        elif hasattr(k, "char") and k.char:
            return k.char.lower()
        return str(k)

    def _on_press(self, key):
        k = self._normalize_key(key)
        self._pressed_keys.add(k)
        trigger_keys = tuple(sorted(self._pressed_keys))
        with self._lock:
            self.cleanup()
            for shortcut, callbacks in list(self.shortcut_callbacks.items()):
                keys = [x.lower() for x in shortcut.split("+")]
                trigger_id = (shortcut, trigger_keys)
                if set(keys).issubset(self._pressed_keys) and trigger_id not in self._already_triggered:
                    for cb, owner_ref, _scope in list(callbacks):
                        real_cb = cb() if isinstance(cb, (weakref.WeakMethod, weakref.ref)) else cb
                        real_owner = owner_ref() if owner_ref else None
                        if real_cb and (owner_ref is None or real_owner):
                            try:
                                real_cb()
                            except Exception as e:
                                print(f"[ShortcutManager] Error in callback {real_cb}: {e}")
                    self._already_triggered.add(trigger_id)

    def _on_release(self, key):
        k = self._normalize_key(key)
        if k in self._pressed_keys:
            self._pressed_keys.remove(k)
        self._already_triggered = {
            (sc, keys) for (sc, keys) in self._already_triggered if k not in keys
        }

    def stop(self):
        with self._lock:
            self.listener.stop()
            self.shortcut_callbacks.clear()
            self._pressed_keys.clear()
            self._already_triggered.clear()

# --- Singleton helpers ---
_shortcut_manager_instance = None

def get_shortcut_manager():
    global _shortcut_manager_instance
    if _shortcut_manager_instance is None:
        _shortcut_manager_instance = ShortcutManager()
        _shortcut_manager_instance.listener.stop()
    return _shortcut_manager_instance

def stop_shortcut_manager():
    global _shortcut_manager_instance
    if _shortcut_manager_instance:
        _shortcut_manager_instance.stop()
        _shortcut_manager_instance = None
