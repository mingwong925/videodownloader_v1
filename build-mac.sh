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

rm -rf dist/.dmg-staging dist/Pianke.dmg
mkdir -p dist/.dmg-staging
cp -R dist/Pianke.app dist/.dmg-staging/Pianke.app
ln -s /Applications dist/.dmg-staging/Applications
hdiutil create -volname "Pianke" -srcfolder dist/.dmg-staging -ov -format UDZO dist/Pianke.dmg >/dev/null
rm -rf dist/.dmg-staging

printf '%s\n' "Built: dist/Pianke.app"
printf '%s\n' "Built: dist/Pianke.dmg"