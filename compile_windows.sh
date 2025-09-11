#!/bin/bash

ENTRYPOINT="main.py"
OUTPUT_DIR="build_output"

# Vyčistí predchádzajúci build
rm -rf "$OUTPUT_DIR"

# Vytvorí adresára ak neexistuje
mkdir -p "$OUTPUT_DIR"

# Kompilácia s podporou PySide6
python -m nuitka \
  --output-dir="$OUTPUT_DIR" \
  --remove-output \
  --plugin-enable=pyside6 \
  --include-module=sqlite3 \
  --include-module=_sqlite3 \
  --windows-console-mode=disable \
  --include-data-dir=assets=assets \
  --standalone \
  "$ENTRYPOINT"

if [ $? -eq 0 ]; then
  echo "Kompilácia úspešná."

  # Skopíruj modules priečinok vedľa spustiteľného súboru
  cp -r modules "$OUTPUT_DIR/$(basename ${ENTRYPOINT%.*})".dist/

  echo "Modules priečinok skopírovaný do $OUTPUT_DIR/$(basename ${ENTRYPOINT%.*}).dist/"
  echo "Spustenie: $OUTPUT_DIR/$(basename ${ENTRYPOINT%.*}).dist/$(basename ${ENTRYPOINT%.*})"
else
  echo "Kompilácia zlyhala"
fi
