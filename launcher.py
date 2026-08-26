from __future__ import annotations

import logging
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add current directory or PyInstaller extracted folder to sys.path
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    base_dir = Path(sys._MEIPASS)
else:
    base_dir = Path(__file__).parent.resolve()

if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

# Ensure standard streams exist when run under --noconsole on Windows
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")
if sys.stdin is None:
    sys.stdin = open(os.devnull, "r")

import uvicorn
from app.config import get_settings
from app.main import app


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def setup_file_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "service.log"
    logging.basicConfig(
        filename=str(log_file),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def open_browser(url: str, delay: float = 1.5) -> None:
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=_open, daemon=True, name="browser-launcher").start()


def main() -> None:
    settings = get_settings()
    host = settings.dashboard_host  # Default "0.0.0.0"
    port = settings.dashboard_port  # Default 8787
    local_ip = get_local_ip()
    local_url = f"http://127.0.0.1:{port}"
    lan_url = f"http://{local_ip}:{port}"

    setup_file_logging(settings.log_dir)
    logging.info("Starting Telegram Media Downloader on %s:%s", host, port)
    logging.info("LAN URL: %s", lan_url)

    is_silent = "--silent" in sys.argv or "--background" in sys.argv
    if not is_silent and "--no-browser" not in sys.argv:
        open_browser(local_url)

    uvicorn.run(app, host=host, port=port, log_level=settings.log_level.lower(), access_log=False)


if __name__ == "__main__":
    main()
