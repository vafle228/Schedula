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
ICON = os.path.join(DESKTOP_STATIC, "icon.ico")  # иконка окна/exe (desktop/static/icon.ico)
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

# Мы всегда запускаемся с gui="qt" (см. desktop/main.py) — это не зависит
# от наличия Edge WebView2 на машине пользователя и одинаково работает
# на Windows и Linux. webview.platforms.qt использует qtpy поверх PyQt6;
# перечисляем только реально используемые Qt-модули (не весь PyQt6 —
# иначе PyInstaller тащит Qt3D/Multimedia/Bluetooth/QML и т.п. и сборка
# раздувается на сотни лишних МБ).
hiddenimports += [
    "webview.platforms.qt", "qtpy",
    "PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets",
    "PyQt6.QtNetwork", "PyQt6.QtWebChannel", "PyQt6.QtPrintSupport",
    "PyQt6.QtWebEngineCore", "PyQt6.QtWebEngineWidgets",
]
_qt_datas, _qt_bins = [], []

hiddenimports = sorted(set(hiddenimports))

# ---------------------------------------------------------------------------
# datas: раскладываем по ФИКСИРОВАННЫМ префиксам, под которые заточен paths.py
# ---------------------------------------------------------------------------
datas = list(_wv_datas) + list(_qt_datas)

# Vue SPA -> 'client/dist' (mirrors resource_path() in desktop/main.py)
if os.path.isdir(CLIENT_DIST):
    datas.append((CLIENT_DIST, os.path.join("client", "dist")))
else:
    raise SystemExit(f"[spec] Не найдена сборка Vue: {CLIENT_DIST}. "
                     f"Сначала выполните `npm run build` в client/.")

# Иконка exe/окна — обязательный ассет.
if not os.path.isfile(ICON):
    raise SystemExit(f"[spec] Не найдена иконка: {ICON}. "
                     f"Положите icon.ico в desktop/static/.")

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
binaries = list(_wv_bins) + list(_qt_bins)

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
        # GUI-бэкенды pywebview, которые точно не используем (используем только PyQt6):
        "PyQt5", "PySide2", "PySide6", "gi", "gtk",
        # Модули PyQt6, которые webview.platforms.qt не использует:
        "PyQt6.Qt3DAnimation", "PyQt6.Qt3DCore", "PyQt6.Qt3DExtras",
        "PyQt6.Qt3DInput", "PyQt6.Qt3DLogic", "PyQt6.Qt3DRender",
        "PyQt6.QtBluetooth", "PyQt6.QtCharts", "PyQt6.QtDataVisualization",
        "PyQt6.QtDesigner", "PyQt6.QtGraphs", "PyQt6.QtGraphsWidgets",
        "PyQt6.QtHelp", "PyQt6.QtMultimedia", "PyQt6.QtMultimediaWidgets",
        "PyQt6.QtNetworkAuth", "PyQt6.QtNfc", "PyQt6.QtOpenGL",
        "PyQt6.QtOpenGLWidgets", "PyQt6.QtPdf", "PyQt6.QtPdfWidgets",
        "PyQt6.QtPositioning", "PyQt6.QtQml",
        "PyQt6.QtQuick", "PyQt6.QtQuick3D", "PyQt6.QtQuickWidgets",
        "PyQt6.QtRemoteObjects", "PyQt6.QtSensors", "PyQt6.QtSerialPort",
        "PyQt6.QtSpatialAudio", "PyQt6.QtSql", "PyQt6.QtStateMachine",
        "PyQt6.QtSvg", "PyQt6.QtSvgWidgets", "PyQt6.QtTest",
        "PyQt6.QtTextToSpeech", "PyQt6.QtWebEngineQuick",
        "PyQt6.QtWebSockets", "PyQt6.QtXml", "PyQt6.uic",
        "PyQt6.QAxContainer", "PyQt6.Qsci",
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
    upx=False,                            # UPX ломает ресурс иконки в .exe (Windows показывает дефолтную) + ложные срабатывания антивируса
    console=False,                        # <-- для отладки True; для релиза False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,                            # см. коммент в EXE: UPX портит иконку/триггерит AV
    upx_exclude=[],
    name="Schedula",
)