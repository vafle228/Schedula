import sys
from pathlib import Path

import webview
import threading

from server.main import build_api
from bottle import template, static_file

api = build_api()


def resource_path(relative: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return str(Path(sys._MEIPASS).joinpath(relative))
    return str(Path(relative))


@api.get("/")
def enter_point():
    return template(resource_path("static/index.html"))


@api.get("/css/<filepath:re:.*\.css>")
def css(filepath: str):
    return static_file(filepath, root=resource_path("static/css"))


@api.get("/nullstyle.css")
def null_style():
    return static_file("nullstyle.css", root=resource_path("static/"))


@api.get("/fonts/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath: str):
    return static_file(filepath, root=resource_path("static/fonts"))


@api.get("/js/<filepath:re:.*\.js>")
def js(filepath: str):
    return static_file(filepath, root=resource_path("static/js"))


if __name__ == "__main__":
    server_thread = threading.Thread(
        target=api.run, daemon=True, kwargs={
            "server": "waitress",
            "host": "127.0.0.1",
            "port": 8000,
            "quiet": True
        }
    )
    webview.create_window("Schedula", url="http://127.0.0.1:8000/")

    server_thread.start()
    webview.start()
    server_thread.join(0)
