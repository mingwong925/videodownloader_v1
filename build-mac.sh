#!/bin/sh
set -eu

python3 -m pip install -r desktop-requirements.txt
python3 -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name Pianke \
  --add-data "static:static" \
  --collect-all imageio_ffmpeg \
  desktop_app.py

printf '%s\n' "Built: dist/Pianke.app"