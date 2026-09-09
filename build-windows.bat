@echo off
setlocal

python -m pip install -r desktop-requirements.txt
python build-icon.py
python -m PyInstaller --noconfirm --clean --windowed --onedir ^
  --name Pianke ^
  --icon assets\icon.ico ^
  --add-data "static;static" ^
  --collect-all imageio_ffmpeg ^
  --collect-all yt_dlp ^
  desktop_app.py

echo Built: dist\Pianke\Pianke.exe