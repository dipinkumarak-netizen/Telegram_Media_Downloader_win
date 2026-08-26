from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import winreg
from pathlib import Path


def kill_running_process() -> None:
    try:
        subprocess.run(["taskkill", "/F", "/IM", "TelegramMediaDownloader.exe"], capture_output=True)
    except Exception:
        pass


def remove_startup_entry() -> None:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, "TelegramMediaDownloader")
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
    except Exception:
        pass


def remove_uninstall_entry() -> None:
    try:
        winreg.DeleteKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Uninstall\TelegramMediaDownloader",
        )
    except Exception:
        pass


def remove_firewall_rule() -> None:
    try:
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "delete", "rule", 'name="Telegram Media Downloader"'],
            capture_output=True,
        )
    except Exception:
        pass


def remove_shortcuts() -> None:
    desktop = Path.home() / "Desktop" / "Telegram Media Downloader.lnk"
    if desktop.exists():
        try:
            desktop.unlink()
        except Exception:
            pass

    start_menu = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Telegram Media Downloader"
    if start_menu.exists():
        try:
            shutil.rmtree(start_menu, ignore_errors=True)
        except Exception:
            pass


def purge_all_data() -> None:
    """Completely delete all session files, settings.json, database, and logs."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        data_dir = Path(local_app_data) / "TelegramMediaDownloader"
        if data_dir.exists():
            try:
                shutil.rmtree(data_dir, ignore_errors=True)
            except Exception:
                pass

    home_local = Path.home() / "AppData" / "Local" / "TelegramMediaDownloader"
    if home_local.exists():
        try:
            shutil.rmtree(home_local, ignore_errors=True)
        except Exception:
            pass


def main() -> None:
    is_silent = "/S" in sys.argv or "/silent" in sys.argv or "--silent" in sys.argv

    if not is_silent:
        root = tk.Tk()
        root.withdraw()

        confirm = messagebox.askyesno(
            "Uninstall Telegram Media Downloader",
            "Are you sure you want to completely uninstall Telegram Media Downloader?\n\n"
            "This will remove all login sessions, credentials, and settings so future installations start completely fresh.\n"
            "(Your downloaded media files in the Downloads folder will NOT be deleted).",
            icon="warning",
        )

        if not confirm:
            return

    kill_running_process()
    remove_startup_entry()
    remove_uninstall_entry()
    remove_firewall_rule()
    remove_shortcuts()
    purge_all_data()

    install_dir = Path.home() / "AppData" / "Local" / "Programs" / "TelegramMediaDownloader"

    if not is_silent:
        messagebox.showinfo(
            "Uninstall Complete",
            "Telegram Media Downloader and all configuration/session data have been completely removed from your system.",
        )

    # Self-delete batch script to remove the installation directory
    cleanup_bat = install_dir.parent / "tmd_cleanup.bat"
    cleanup_bat.write_text(f"""@echo off
timeout /t 2 /nobreak > NUL
rmdir /s /q "{install_dir}"
del "%~f0"
""")
    subprocess.Popen([str(cleanup_bat)], shell=True, creationflags=0x08000000)


if __name__ == "__main__":
    main()
