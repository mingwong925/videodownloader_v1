#!/bin/sh
set -eu

python3 -m pip install -r desktop-requirements.txt
test -f assets/icon.icns
python3 -m PyInstaller --noconfirm --clean --windowed --onedir \
  --name Pianke \
  --icon assets/icon.icns \
  --add-data "static:static" \
  --add-data "assets/icon-source.png:assets" \
  --collect-all imageio_ffmpeg \
  --collect-all yt_dlp \
  desktop_app.py

printf '%s\n' "Built: dist/Pianke.app"