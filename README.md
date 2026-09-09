# 抓片 / Universal Video Downloader

以 FastAPI 和 yt-dlp 建立的本機影片下載工具，支援公開的 YouTube、Instagram、Facebook、X/Twitter、TikTok、抖音與 bilibili 連結。

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

## Render 部署

專案已附上 `render.yaml`。將專案推送到 GitHub 後，在 Render 選擇 **New + > Blueprint**，連接該 repository，Render 會依照設定建立 Web Service。

注意：Render Free Service 會休眠，且本機 `downloads/` 不是永久儲存空間；服務重啟後已下載檔案可能消失。大型或長時間下載建議使用付費服務或外部物件儲存。
