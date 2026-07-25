import sys
import threading
from pathlib import Path

import webview
from bottle import static_file

from desktop.utils.download import DownloadApi
from server.main import build_api

api = build_api()


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS).joinpath(relative))
    return str(Path(__file__).resolve().parent.parent.joinpath(relative))

@api.get("/")
def enter_point():
    return static_file("index.html", root=resource_path("client/dist"))

@api.get("/assets/<filepath:path>")
def assets(filepath: str):
    return static_file(filepath, root=resource_path("client/dist/assets"))

@api.get("/<filepath:path>")
def spa_fallback(filepath: str):
    return static_file("index.html", root=resource_path("client/dist"))


if __name__ == "__main__":
    server_thread = threading.Thread(
        target=api.run, daemon=True, kwargs={
            "server": "waitress",
            "host": "127.0.0.1",
            "port": 8000,
            "quiet": True
        }
    )
    server_thread.start()

    js_api = DownloadApi()
    window = webview.create_window(
        "Schedula",
        url="http://127.0.0.1:8000/",
        js_api=js_api,
        min_size=(1500, 800))
    js_api._window = window

    webview.start(gui="edgechromium" if sys.platform == "win32" else "qt")
