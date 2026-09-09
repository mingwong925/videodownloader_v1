from pathlib import Path

from PIL import Image

source = Image.open(Path("assets") / "icon-source.png").convert("RGBA")
source.save(Path("assets") / "icon.ico", format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("Built: assets/icon.ico")
