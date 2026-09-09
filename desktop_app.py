from __future__ import annotations

import socket
import threading
import time

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


def main() -> None:
    port = get_free_port()
    server = Server(Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    wait_for_server(port)
    webview.create_window("片刻 | 萬用影片下載器", f"http://127.0.0.1:{port}", width=1120, height=820, min_size=(720, 600))
    webview.start()
    server.should_exit = True


if __name__ == "__main__":
    main()