import sys
import threading
from pathlib import Path

import webview
from bottle import static_file

from server.main import build_api

api = build_api()


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS).joinpath(relative))
    return str(Path(__file__).resolve().parent.parent.joinpath(relative))


@api.get("/")
def enter_point():
    return static_file("index.html", root=resource_path("client"))


@api.get("/css/<filepath:re:.*\\.css>")
def css(filepath: str):
    return static_file(filepath, root=resource_path("client/css"))


@api.get("/nullstyle.css")
def null_style():
    return static_file("nullstyle.css", root=resource_path("client/"))


@api.get("/fonts/<filepath:re:.*\\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath: str):
    return static_file(filepath, root=resource_path("client/fonts"))


@api.get("/js/<filepath:re:.*\\.js>")
def js(filepath: str):
    return static_file(filepath, root=resource_path("client/js"))


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
    window = webview.create_window(
        "Schedula",
        url="http://127.0.0.1:8000/",
        width=1640,
        height=900,
        maximized=False,
        resizable=False)
    webview.start(gui="qt")
