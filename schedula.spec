# -*- mode: python ; coding: utf-8 -*-
# Сборка:  pyinstaller schedula.spec --noconfirm
# Отладка: сначала собирайте с console=True (в блоке EXE), чтобы видеть traceback.
import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

# ---------------------------------------------------------------------------
# Корень проекта. spec ДОЛЖЕН лежать в корне рядом с pyproject.toml.
# ---------------------------------------------------------------------------
ROOT = os.path.abspath(globals().get("SPECPATH", os.getcwd()))
DESKTOP = os.path.join(ROOT, "desktop")
SERVER = os.path.join(ROOT, "server")
CLIENT_DIST = os.path.join(ROOT, "client", "dist")
DESKTOP_STATIC = os.path.join(DESKTOP, "static")
DB_TEMPLATE = os.path.join(SERVER, "schedula.db")
ENV_FILE = os.path.join(ROOT, ".env")
ICON = os.path.join(DESKTOP_STATIC, "icon.ico")  # оставьте, если есть иконка окна/exe
SERVER_TEMPLATES = os.path.join(SERVER, "api", "services", "templates")

# ---------------------------------------------------------------------------
# Делаем пакеты импортируемыми ДЛЯ АНАЛИЗАТОРА PyInstaller, чтобы
# collect_submodules смог их обойти. На рантайм это не влияет.
# ---------------------------------------------------------------------------
for _p in (ROOT, SERVER, DESKTOP):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# hiddenimports: покрываем обе схемы импортов внутри server/
#   - пакетную  (from server.core import ...)
#   - top-level (from core import ...)  — на случай sys.path-хака в dev
# То же самое для desktop.utils.
# ---------------------------------------------------------------------------
hiddenimports = []
for _mod in (
    "server", "api", "core", "infrastructure", "schedule",
    "desktop", "utils", "desktop.utils",
    "bottle",
):
    try:
        hiddenimports += collect_submodules(_mod)
    except Exception:
        pass

# pywebview: забираем всё — js-ассеты, платформенные бэкенды, dll.
_wv_datas, _wv_bins, _wv_hidden = collect_all("webview")
hiddenimports += _wv_hidden

# Бэкенды/зависимости pywebview на Windows (часть может отсутствовать — это ок).
for _opt in ("comtypes", "clr", "webview.platforms.edgechromium",
             "webview.platforms.mshtml", "webview.platforms.cef"):
    hiddenimports.append(_opt)

hiddenimports = sorted(set(hiddenimports))

# ---------------------------------------------------------------------------
# datas: раскладываем по ФИКСИРОВАННЫМ префиксам, под которые заточен paths.py
# ---------------------------------------------------------------------------
datas = list(_wv_datas)

# Vue SPA -> 'client/dist' (mirrors resource_path() in desktop/main.py)
if os.path.isdir(CLIENT_DIST):
    datas.append((CLIENT_DIST, os.path.join("client", "dist")))
else:
    raise SystemExit(f"[spec] Не найдена сборка Vue: {CLIENT_DIST}. "
                     f"Сначала выполните `npm run build` в client/.")

# desktop-статика (иконка и т.п.) -> 'desktop/static'
if os.path.isdir(DESKTOP_STATIC):
    datas.append((DESKTOP_STATIC, os.path.join("desktop", "static")))

# Шаблон БД -> 'db_template/schedula.db'
if os.path.isfile(DB_TEMPLATE):
    datas.append((DB_TEMPLATE, "db_template"))

# Excel-шаблоны сервера -> 'server_templates'
if os.path.isdir(SERVER_TEMPLATES):
    datas.append((SERVER_TEMPLATES, "server_templates"))

# .env опционально (если сервер читает его через python-dotenv из cwd/ресурса)
if os.path.isfile(ENV_FILE):
    datas.append((ENV_FILE, "."))

# ---------------------------------------------------------------------------
# binaries: на всякий случай (sqlite3.dll и пр. PyInstaller обычно тащит сам)
# ---------------------------------------------------------------------------
binaries = list(_wv_bins)

# ===========================================================================
a = Analysis(
    [os.path.join(DESKTOP, "main.py")],
    pathex=[ROOT, SERVER, DESKTOP],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # выкидываем тяжёлое/ненужное из client-тулчейна, если вдруг подтянется
        "tkinter", "unittest", "pytest",
        # GUI-бэкенды pywebview, которые точно не используем на Windows:
        "PyQt5", "PyQt6", "PySide2", "PySide6", "gi", "gtk",
        "webview.platforms.qt", "qtpy",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],                                   # в onedir сюда ничего не кладём
    exclude_binaries=True,
    name="Schedula",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,                         # <-- для отладки True; для релиза False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON if os.path.isfile(ICON) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Schedula",
)