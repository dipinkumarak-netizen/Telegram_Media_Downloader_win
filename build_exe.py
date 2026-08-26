from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def build():
    root = Path(__file__).parent.resolve()
    dist_dir = root / "dist"
    templates_dir = root / "app" / "templates"
    version_file = root / "VERSION"

    print("=" * 70)
    print("  Building Telegram Media Downloader for Windows 11")
    print("=" * 70)

    # Terminate running instances to release file locks
    subprocess.run(["taskkill", "/F", "/IM", "TelegramMediaDownloader.exe"], capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "uninstall.exe"], capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "TelegramMediaDownloader_Setup.exe"], capture_output=True)

    # 1. Build Main Application Executable (Windowless Background Runner)
    print("\n[Step 1/3] Building Windowless Background Executable (TelegramMediaDownloader.exe)...")
    main_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--noconsole",  # No command window / windowless background execution!
        "--name",
        "TelegramMediaDownloader",
        f"--add-data={templates_dir};app/templates",
        f"--add-data={version_file};.",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespans",
        "--hidden-import=uvicorn.lifespans.on",
        "--hidden-import=aiosqlite",
        "--hidden-import=argon2",
        "--hidden-import=cryptg",
        "--hidden-import=app.services.fast_telethon",
        "--hidden-import=telethon",
        "--hidden-import=telethon.tl.types",
        "--hidden-import=jinja2",
        "--hidden-import=markupsafe",
        "--collect-all=jinja2",
        "--collect-all=starlette",
        "--hidden-import=pydantic_settings",
        str(root / "launcher.py"),
    ]
    res1 = subprocess.run(main_args, cwd=str(root))
    if res1.returncode != 0:
        print(f"[FAIL] Failed to build TelegramMediaDownloader.exe (code {res1.returncode})")
        sys.exit(res1.returncode)

    # 2. Build Uninstaller Executable
    print("\n[Step 2/3] Building Uninstaller Executable (uninstall.exe)...")
    uninstall_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        "--name",
        "uninstall",
        str(root / "uninstaller.py"),
    ]
    res2 = subprocess.run(uninstall_args, cwd=str(root))
    if res2.returncode != 0:
        print(f"[FAIL] Failed to build uninstall.exe (code {res2.returncode})")
        sys.exit(res2.returncode)

    # 3. Build Setup Installer Executable
    print("\n[Step 3/3] Building Standalone Setup Installer (TelegramMediaDownloader_Setup.exe)...")
    installer_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        "--name",
        "TelegramMediaDownloader_Setup",
        f"--add-data={dist_dir / 'TelegramMediaDownloader.exe'};.",
        f"--add-data={dist_dir / 'uninstall.exe'};.",
        f"--add-data={root / 'allow_firewall_as_admin.bat'};.",
        f"--add-data={templates_dir};app/templates",
        f"--add-data={version_file};.",
        str(root / "installer.py"),
    ]
    res3 = subprocess.run(installer_args, cwd=str(root))
    if res3.returncode != 0:
        print(f"[FAIL] Failed to build TelegramMediaDownloader_Setup.exe (code {res3.returncode})")
        sys.exit(res3.returncode)

    setup_exe = dist_dir / "TelegramMediaDownloader_Setup.exe"
    main_exe = dist_dir / "TelegramMediaDownloader.exe"

    print("\n" + "=" * 70)
    print("  ALL BUILDS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"  Setup Installer (.exe): {setup_exe}")
    print(f"     Size: {setup_exe.stat().st_size / (1024*1024):.2f} MB")
    print(f"  Standalone App (.exe):  {main_exe}")
    print(f"     Size: {main_exe.stat().st_size / (1024*1024):.2f} MB")
    print("=" * 70)


if __name__ == "__main__":
    build()
