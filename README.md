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
