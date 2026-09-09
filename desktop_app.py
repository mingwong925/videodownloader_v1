from __future__ import annotations

import socket
import shutil
import sys
import threading
import time
from pathlib import Path

if "--yt-dlp" in sys.argv:
    sys.argv.remove("--yt-dlp")
    import yt_dlp

    yt_dlp.main()
    raise SystemExit

import webview
from uvicorn import Config, Server

from app import DOWNLOAD_DIR, app, jobs, jobs_lock


def get_free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(port: int) -> None:
    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("本機下載服務啟動失敗")


class DesktopApi:
    def __init__(self, port: int) -> None:
        self.port = port
        self.window = None

    def save_file(self, job_id: str, filename: str) -> str:
        with jobs_lock:
            job = jobs.get(job_id)
        source_name = str(job.get("filename")) if job else filename
        source = DOWNLOAD_DIR / Path(source_name).name
        if not source.is_file():
            raise FileNotFoundError(f"找不到已完成檔案：{source.name}")
        safe_name = Path(source_name).name or f"pianke-{job_id}.mp4"
        if self.window is None:
            raise RuntimeError("桌面視窗尚未準備完成")
        selected = self.window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=str(Path.home() / "Downloads"),
            save_filename=safe_name,
        )
        if not selected:
            return ""
        destination = Path(selected[0] if isinstance(selected, (list, tuple)) else selected)
        shutil.copyfile(source, destination)
        return str(destination)


def main() -> None:
    port = get_free_port()
    server = Server(Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    wait_for_server(port)
    desktop_api = DesktopApi(port)
    window = webview.create_window("片刻 | 萬用影片下載器", f"http://127.0.0.1:{port}", js_api=desktop_api, width=1120, height=820, min_size=(720, 600))
    desktop_api.window = window
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()