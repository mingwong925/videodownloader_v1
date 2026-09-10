# 片刻影片下載

Copyright © 2026 Ming Wong.

以 FastAPI 和 yt-dlp 建立的本機影片下載工具，支援公開的 YouTube、Instagram、Facebook、X/Twitter、TikTok、抖音、bilibili、Pinterest、Vimeo、Dailymotion、Twitch、SoundCloud、小紅書、微博、快手與 Threads 連結。

## 啟動

需要 Python 3.10+；`imageio-ffmpeg` 會隨 Python 依賴提供影片合併與 MP3 轉檔所需的 FFmpeg。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

開啟 http://127.0.0.1:8000。

部分平台內容需要登入、年齡驗證或不是公開內容，這類網址不會被繞過；請只下載你有權使用的內容。

## 桌面 App（Mac / Windows）

桌面版會在你的電腦啟動本機下載服務，影片直接存到本機 `downloads/`，不需要 Render。

桌面 App 啟動後會常駐 macOS Menu Bar 或 Windows system tray；從「片刻」圖示可以重新開啟下載視窗或退出 App。

在 macOS 建置：

```bash
chmod +x build-mac.sh
./build-mac.sh
open dist/Pianke.app
```

在 Windows 建置：

```bat
build-windows.bat
```

Windows 輸出位置是 `dist\\Pianke\\Pianke.exe`。Mac 建置必須在 Mac 執行，Windows 建置必須在 Windows 執行；建置腳本會把網站資產、yt-dlp 與 FFmpeg 一起打包。

App icon 來源是 `assets/icon-source.png`，建置時會套用到 macOS App、Windows App 與 Windows 安裝程式。

## 安裝檔

GitHub Actions 的 `Build Desktop Installers` workflow 會自動建立：

- macOS：`Pianke.dmg`
- Windows：`Pianke-Setup.exe`

在 GitHub repository 的 **Actions** 頁面手動執行 workflow，完成後從 **Artifacts** 下載對應安裝檔；也可以建立 `v1.0.0` 之類的 tag 觸發建置。

## Render 部署

專案已附上 `render.yaml`。將專案推送到 GitHub 後，在 Render 選擇 **New + > Blueprint**，連接該 repository，Render 會依照設定建立 Web Service。

注意：Render Free Service 會休眠，且本機 `downloads/` 不是永久儲存空間；服務重啟後已下載檔案可能消失。大型或長時間下載建議使用付費服務或外部物件儲存。
