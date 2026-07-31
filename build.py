#!/usr/bin/env python3
"""Full build: 'npm run build' for the client SPA, then PyInstaller packing.

Cross-platform (Windows/Linux) - run with:
    python build.py
    uv run build.py
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CLIENT = ROOT / "client"


def run(cmd, cwd=None):
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def require(name: str) -> str:
    exe = shutil.which(name)
    if exe is None:
        sys.exit(f"'{name}' not found on PATH.")
    return exe


def build_client(skip_install: bool):
    npm = require("npm")
    if not skip_install:
        run([npm, "install"], cwd=CLIENT)
    run([npm, "run", "build"], cwd=CLIENT)


def build_desktop(clean: bool):
    base = ["uv", "run", "pyinstaller"] if shutil.which("uv") else [sys.executable, "-m", "PyInstaller"]
    cmd = base + ["schedula.spec", "--noconfirm"]
    if clean:
        cmd.append("--clean")
    run(cmd, cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-client", action="store_true", help="Skip the npm build and reuse existing client/dist")
    parser.add_argument("--skip-npm-install", action="store_true", help="Skip 'npm install', only run 'npm run build'")
    parser.add_argument("--clean", action="store_true", help="Pass --clean to PyInstaller")
    args = parser.parse_args()

    if not args.skip_client:
        build_client(args.skip_npm_install)
    build_desktop(args.clean)
    print(f"\nBuild finished -> {ROOT / 'dist' / 'Schedula'}")


if __name__ == "__main__":
    main()
