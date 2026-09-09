@echo off
setlocal

python -m pip install -r desktop-requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --onedir ^
  --name Pianke ^
  --add-data "static;static" ^
  --collect-all imageio_ffmpeg ^
  --collect-all yt_dlp ^
  desktop_app.py

echo Built: dist\Pianke\Pianke.exe