from __future__ import annotations

import socket
import sys
import threading
import time
import urllib.request
from pathlib import Path

if "--yt-dlp" in sys.argv:
    sys.argv.remove("--yt-dlp")
    import yt_dlp

    yt_dlp.main()
    raise SystemExit

import webview
from uvicorn import Config, Server

from app import app


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

    def download_file(self, job_id: str, filename: str) -> str:
        downloads = Path.home() / "Downloads"
        downloads.mkdir(exist_ok=True)
        safe_name = Path(filename).name or f"pianke-{job_id}.mp4"
        destination = downloads / safe_name
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/file/{job_id}") as response:
            destination.write_bytes(response.read())
        return str(destination)


def main() -> None:
    port = get_free_port()
    server = Server(Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    wait_for_server(port)
    webview.create_window("片刻 | 萬用影片下載器", f"http://127.0.0.1:{port}", js_api=DesktopApi(port), width=1120, height=820, min_size=(720, 600))
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()