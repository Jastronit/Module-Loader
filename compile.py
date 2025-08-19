import os
import shutil
import subprocess
import sys

ENTRYPOINT = "main.py"
OUTPUT_DIR = "build_output"
DIST_NAME = os.path.splitext(os.path.basename(ENTRYPOINT))[0]

def main():
    # Vyčisti predchádzajúci build
    if os.path.exists(OUTPUT_DIR):
        print(f"Odstraňujem starý build: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    # Spusti Nuitka
    cmd = [
        sys.executable, "-m", "nuitka",
        f"--output-dir={OUTPUT_DIR}",
        "--remove-output",
        "--plugin-enable=pyside6",
        "--include-module=sqlite3",
        "--include-module=_sqlite3",
        "--include-data-dir=assets=assets",
        "--standalone",
        ENTRYPOINT,
    ]

    print("Spúšťam Nuitka:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("❌ Kompilácia zlyhala")
        sys.exit(1)

    print("✅ Kompilácia úspešná.")

    # Skopíruj modules priečinok
    dist_path = os.path.join(OUTPUT_DIR, f"{DIST_NAME}.dist")
    modules_src = "modules"
    modules_dst = os.path.join(dist_path, "modules")

    if os.path.exists(modules_src):
        shutil.copytree(modules_src, modules_dst, dirs_exist_ok=True)
        print(f"📂 Modules priečinok skopírovaný do {modules_dst}")

    print(f"▶️ Spustenie: {os.path.join(dist_path, DIST_NAME)}")

if __name__ == "__main__":
    main()
