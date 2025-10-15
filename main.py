# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Importovanie potrebných knižníc a nastavenie ciest ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- Importovanie potrebných knižníc pre moduly ----////
import os
import sys
import importlib.util
import threading
import subprocess
import platform
import atexit
import gui_main

from glob import glob
# ////-----------------------------------------------------------------------------------------

# ////---- Načítanie cesty k modulu ----////
MODULES_DIR = "modules"

# Zaručíme, že cesta k modulu je v sys.path, aby sme mohli importovať moduly po skompilovaní
module_path = os.path.join(os.path.dirname(__file__), "modules")
if module_path not in sys.path:
    sys.path.append(module_path)
# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Funkcie na načítanie a spustenie logiky modulov ----////
# /////////////////////////////////////////////////////////////////////////////////////////////

# ////---- Nájdenie logiky v python zložke ----////
def find_logic_py(module_path):
    logic_path = os.path.join(module_path, "python", "logic.py")
    return logic_path if os.path.isfile(logic_path) else None
# ////-----------------------------------------------------------------------------------------

# ////---- Spustenie Python logiky ----////
def run_python_logic(logic_path, stop_event):
    try:
        # Dynamické načítanie modulu z daného súboru
        spec = importlib.util.spec_from_file_location("logic", logic_path)
        logic = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logic)

        # Spustenie logiky
        if hasattr(logic, "logic_main_init"):
            logic.logic_main_init(stop_event=stop_event)
        elif hasattr(logic, "main"):
            logic.main()
    except Exception as e:
        print(f"Chyba pri spustení logiky {logic_path}: {e}")
    # else: nothing to run
# ////-----------------------------------------------------------------------------------------

# ////---- Spustenie binárneho súboru ----////
# Poznámka: Toto je pozastavené, pretože open-source moduly by mali používať Python logiku
def run_binary(module_path):
    system = platform.system().lower()
    if system == "windows":
        bin_path = os.path.join(module_path, "bin", "windows", "app.exe")
    else:
        bin_path = os.path.join(module_path, "bin", "linux", "app.bin")
    if os.path.isfile(bin_path):
        subprocess.Popen([bin_path])
    else:
        print(f"Nenašiel sa žiadny spustiteľný súbor v {module_path}")
# ////-----------------------------------------------------------------------------------------

# ////---- Funkcia pre ukončenie všetkých logík ----////
def stop_all_logics(stop_events, logic_threads, exit_app=False):
    for stop_event in stop_events:
        stop_event.set()  # Nastavenie stop_event, čo ukončí bežiacu logiku
    for thread in logic_threads:
        thread.join()  # Čakáme na ukončenie vlákien
    print("Všetky logiky boli ukončené.")
    if exit_app:
        sys.exit(0)  # Ukončíme aplikáciu
# ////-----------------------------------------------------------------------------------------

# /////////////////////////////////////////////////////////////////////////////////////////////
# ////---- Hlavná funkcia pre spustenie GUI a logiky modulov ----////
# /////////////////////////////////////////////////////////////////////////////////////////////
def main():
    # Získanie všetkých ciest k modulom v adresári modules
    module_paths = [os.path.dirname(p) for p in glob(os.path.join(MODULES_DIR, "*", "python", "logic.py"))]
    all_modules = [os.path.join(MODULES_DIR, d) for d in os.listdir(MODULES_DIR) if os.path.isdir(os.path.join(MODULES_DIR, d))]

    stop_events = []  # Uchová stop_events pre každý modul
    logic_threads = []  # Uchová referencie na vlákna

    # Zaregistrujeme ukončenie všetkých logík pri ukončení programu
    atexit.register(lambda: stop_all_logics(stop_events, logic_threads, exit_app=False))
    
    # Spúšťanie nezávyslej logiky pre každý modul
    for module_path in all_modules:
        logic_py = find_logic_py(module_path)
        # Ak existuje python logika v module, spustíme ju
        if logic_py:
            print(f"Načítavam Python logiku: {logic_py}")

            # Vytvorenie stop_event pre tento modul
            stop_event = threading.Event()
            stop_events.append(stop_event)
            
            # Spustenie logiky v samostatnom vlákne
            logic_thread = threading.Thread(target=run_python_logic, args=(logic_py, stop_event))
            logic_thread.start()
            logic_threads.append(logic_thread)

        # Ak neexistuje python logika, skúšame spustiť binárku (pozastavené pre open-source pristup)
        #else:
        #    print(f"Python logika nenájdená v {module_path}, skúšam binárku...")
        #    run_binary(module_path)

    return stop_events, logic_threads
# ////-----------------------------------------------------------------------------------------

# ////---- Volanie hlavnej funkcie ----////
if __name__ == "__main__":

    # Spustiť logiku modulov
    stop_events, logic_threads = main()

    # Spustiť GUI aplikáciu
    if "--nogui" not in sys.argv: # Spustiť GUI, ak nie je zadaný parameter --nogui
        # Spustiť GUI aplikáciu s callbackom na ukončenie main.py
        gui_main.main(on_close_callback=lambda: stop_all_logics(stop_events, logic_threads, exit_app=True))
# ////-----------------------------------------------------------------------------------------
