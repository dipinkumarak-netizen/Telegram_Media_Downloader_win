from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
from pathlib import Path

# Embedded or bundled path resolution
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BUNDLE_DIR = Path(__file__).parent.resolve()


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def default_install_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Programs" / "TelegramMediaDownloader"
    return Path.home() / "AppData" / "Local" / "Programs" / "TelegramMediaDownloader"


def create_windows_shortcut(target_exe: Path, shortcut_path: Path, description: str = "Telegram Media Downloader", arguments: str = "") -> None:
    try:
        shortcut_path.parent.mkdir(parents=True, exist_ok=True)
        ps_command = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_exe}'
$Shortcut.Arguments = '{arguments}'
$Shortcut.WorkingDirectory = '{target_exe.parent}'
$Shortcut.Description = '{description}'
$Shortcut.Save()
"""
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], capture_output=True, check=False)
    except Exception:
        pass


def register_startup(exe_path: Path) -> None:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "TelegramMediaDownloader", 0, winreg.REG_SZ, f'"{exe_path}" --background')
        winreg.CloseKey(key)
    except Exception:
        pass


def register_uninstall(install_dir: Path, uninstaller_path: Path) -> None:
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\TelegramMediaDownloader"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Telegram Media Downloader")
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Dipin a k")
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_path}"')
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(install_dir / "TelegramMediaDownloader.exe"))
        winreg.CloseKey(key)
    except Exception:
        pass


def configure_firewall_rule() -> None:
    try:
        subprocess.run(
            [
                "netsh", "advfirewall", "firewall", "add", "rule",
                'name=Telegram Media Downloader',
                "dir=in", "action=allow", "protocol=TCP", "localport=8787", "profile=any"
            ],
            capture_output=True,
            check=False,
        )
    except Exception:
        pass


def purge_data_directory() -> None:
    """Purge old session, database, and settings data to start fresh."""
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


def perform_installation(
    install_dir: Path,
    auto_start: bool,
    allow_lan_firewall: bool,
    desktop_shortcut: bool,
    start_menu_shortcut: bool,
    launch_now: bool,
    clean_data: bool = False,
    progress_callback=None,
) -> tuple[bool, str]:
    try:
        if progress_callback:
            progress_callback(10, "Stopping existing processes if running...")
        subprocess.run(["taskkill", "/F", "/IM", "TelegramMediaDownloader.exe"], capture_output=True)

        if clean_data:
            if progress_callback:
                progress_callback(18, "Clearing previous login & session data...")
            purge_data_directory()

        if progress_callback:
            progress_callback(25, "Creating destination folders...")
        install_dir.mkdir(parents=True, exist_ok=True)

        target_main_exe = install_dir / "TelegramMediaDownloader.exe"
        target_uninstall_exe = install_dir / "uninstall.exe"

        if progress_callback:
            progress_callback(40, "Copying program files...")

        # Find main executable in bundle or dist
        source_main = BUNDLE_DIR / "TelegramMediaDownloader.exe"
        if not source_main.exists():
            source_main = BUNDLE_DIR / "dist" / "TelegramMediaDownloader.exe"
        if not source_main.exists():
            source_main = Path(__file__).parent / "dist" / "TelegramMediaDownloader.exe"

        if source_main.exists():
            shutil.copy2(source_main, target_main_exe)
        else:
            launcher_src = BUNDLE_DIR / "launcher.py"
            if launcher_src.exists():
                shutil.copy2(launcher_src, install_dir / "launcher.py")

        # Copy uninstall script or executable
        source_uninstall = BUNDLE_DIR / "uninstall.exe"
        if not source_uninstall.exists():
            source_uninstall = BUNDLE_DIR / "dist" / "uninstall.exe"
        if source_uninstall.exists():
            shutil.copy2(source_uninstall, target_uninstall_exe)
        else:
            uninstaller_py = BUNDLE_DIR / "uninstaller.py"
            if uninstaller_py.exists():
                shutil.copy2(uninstaller_py, install_dir / "uninstaller.py")

        # Copy firewall helper script
        fw_src = BUNDLE_DIR / "allow_firewall_as_admin.bat"
        if not fw_src.exists():
            fw_src = Path(__file__).parent / "allow_firewall_as_admin.bat"
        if fw_src.exists():
            shutil.copy2(fw_src, install_dir / "allow_firewall_as_admin.bat")

        # Copy templates & resources if available
        templates_src = BUNDLE_DIR / "app" / "templates"
        if templates_src.exists():
            dest_templates = install_dir / "app" / "templates"
            dest_templates.mkdir(parents=True, exist_ok=True)
            for item in templates_src.glob("*.html"):
                shutil.copy2(item, dest_templates / item.name)

        if progress_callback:
            progress_callback(60, "Configuring Windows Startup & Shortcuts...")

        if auto_start and target_main_exe.exists():
            register_startup(target_main_exe)

        register_uninstall(install_dir, target_uninstall_exe if target_uninstall_exe.exists() else install_dir / "uninstaller.py")

        if desktop_shortcut and target_main_exe.exists():
            create_windows_shortcut(
                target_main_exe,
                Path.home() / "Desktop" / "Telegram Media Downloader.lnk",
                "Telegram Media Downloader Web Dashboard",
            )

        if start_menu_shortcut and target_main_exe.exists():
            start_menu_folder = (
                Path(os.environ.get("APPDATA", ""))
                / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Telegram Media Downloader"
            )
            create_windows_shortcut(
                target_main_exe,
                start_menu_folder / "Telegram Media Downloader.lnk",
                "Telegram Media Downloader",
            )
            if target_uninstall_exe.exists():
                create_windows_shortcut(
                    target_uninstall_exe,
                    start_menu_folder / "Uninstall Telegram Media Downloader.lnk",
                    "Uninstall Telegram Media Downloader",
                )

        if progress_callback:
            progress_callback(80, "Configuring Windows Firewall for LAN access...")

        if allow_lan_firewall:
            configure_firewall_rule()

        if progress_callback:
            progress_callback(95, "Starting background service...")

        if launch_now and target_main_exe.exists():
            subprocess.Popen(
                [str(target_main_exe), "--background"],
                cwd=str(install_dir),
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )

        if progress_callback:
            progress_callback(100, "Installation complete!")

        return True, "Installation successfully completed!"
    except Exception as exc:
        return False, str(exc)


class InstallerGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Telegram Media Downloader Setup - Windows 11")
        self.root.geometry("590x540")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b111c")

        self.install_dir = default_install_dir()
        self.local_ip = get_local_ip()

        self.setup_styles()
        self.build_ui()

    def setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TProgressbar",
            troughcolor="#1e293b",
            background="#22c55e",
            darkcolor="#22c55e",
            lightcolor="#22c55e",
            bordercolor="#1e293b",
        )

    def build_ui(self) -> None:
        # Header banner
        header = tk.Frame(self.root, bg="#111827", height=86)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_lbl = tk.Label(
            header,
            text="⚡ Telegram Media Downloader",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#111827",
        )
        title_lbl.pack(anchor="w", padx=20, pady=(10, 1))

        sub_lbl = tk.Label(
            header,
            text="Windows 11 Background Service & Remote LAN Access",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#111827",
        )
        sub_lbl.pack(anchor="w", padx=20)

        credit_lbl = tk.Label(
            header,
            text="Created by : Dipin a k",
            font=("Segoe UI", 8),
            fg="#64748b",
            bg="#111827",
        )
        credit_lbl.pack(anchor="w", padx=20, pady=(1, 0))

        # Content container
        self.content_frame = tk.Frame(self.root, bg="#0b111c", padx=24, pady=14)
        self.content_frame.pack(fill="both", expand=True)

        info_box = tk.Frame(self.content_frame, bg="#172033", bd=1, relief="solid")
        info_box.pack(fill="x", pady=(0, 10), ipady=6, ipadx=10)

        info_text = (
            "✨ Installs Telegram Media Downloader as a silent background application.\n"
            f"🌐 Remote LAN Access URL: http://{self.local_ip}:8787\n"
            "🖥️ No command window will pop up; runs quietly in the background."
        )
        tk.Label(
            info_box,
            text=info_text,
            font=("Segoe UI", 9),
            fg="#e2e8f0",
            bg="#172033",
            justify="left",
        ).pack(anchor="w", padx=6)

        # Checkbox options
        self.var_autostart = tk.BooleanVar(value=True)
        self.var_firewall = tk.BooleanVar(value=True)
        self.var_desktop = tk.BooleanVar(value=True)
        self.var_startmenu = tk.BooleanVar(value=True)
        self.var_launch = tk.BooleanVar(value=True)
        self.var_cleandata = tk.BooleanVar(value=False)

        opts_frame = tk.Frame(self.content_frame, bg="#0b111c")
        opts_frame.pack(fill="x", pady=2)

        self.create_check(opts_frame, " Start automatically when Windows boots up (Auto-Start)", self.var_autostart)
        self.create_check(opts_frame, " Allow access from other devices on Local Network (Windows Firewall rule for port 8787)", self.var_firewall)
        self.create_check(opts_frame, " Create Desktop shortcut", self.var_desktop)
        self.create_check(opts_frame, " Create Start Menu shortcut", self.var_startmenu)
        self.create_check(opts_frame, " Start Telegram Media Downloader in background immediately", self.var_launch)
        self.create_check(opts_frame, " Clean Install: Clear any previous login sessions & start fresh", self.var_cleandata)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.content_frame, style="TProgressbar", length=540, mode="determinate")
        self.status_lbl = tk.Label(self.content_frame, text="Ready to install.", font=("Segoe UI", 9), fg="#94a3b8", bg="#0b111c")

        # Footer actions
        footer = tk.Frame(self.root, bg="#111827", height=60)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.btn_cancel = tk.Button(
            footer,
            text="Cancel",
            font=("Segoe UI", 9),
            bg="#223048",
            fg="#e2e8f0",
            activebackground="#2d3f5e",
            activeforeground="#ffffff",
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.root.destroy,
        )
        self.btn_cancel.pack(side="right", padx=(8, 20), pady=14)

        self.btn_install = tk.Button(
            footer,
            text="Install Now ⚡",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.start_install_thread,
        )
        self.btn_install.pack(side="right", pady=14)

    def create_check(self, parent, text, var):
        chk = tk.Checkbutton(
            parent,
            text=text,
            variable=var,
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0b111c",
            activebackground="#0b111c",
            activeforeground="#ffffff",
            selectcolor="#172033",
            anchor="w",
        )
        chk.pack(fill="x", pady=2)
        return chk

    def start_install_thread(self) -> None:
        self.btn_install.config(state="disabled")
        self.btn_cancel.config(state="disabled")
        self.progress_bar.pack(fill="x", pady=(10, 4))
        self.status_lbl.pack(anchor="w")

        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self) -> None:
        def update_progress(val, text):
            self.root.after(0, lambda: self.progress_bar.config(value=val))
            self.root.after(0, lambda: self.status_lbl.config(text=text))

        success, message = perform_installation(
            install_dir=self.install_dir,
            auto_start=self.var_autostart.get(),
            allow_lan_firewall=self.var_firewall.get(),
            desktop_shortcut=self.var_desktop.get(),
            start_menu_shortcut=self.var_startmenu.get(),
            launch_now=self.var_launch.get(),
            clean_data=self.var_cleandata.get(),
            progress_callback=update_progress,
        )

        self.root.after(0, lambda: self.finish_screen(success, message))

    def finish_screen(self, success: bool, message: str) -> None:
        if success:
            self.status_lbl.config(text="✅ Installation Complete!", fg="#22c55e", font=("Segoe UI", 10, "bold"))
            self.btn_cancel.pack_forget()
            self.btn_install.config(
                text="Finish & Open Dashboard",
                state="normal",
                bg="#22c55e",
                command=self.finish_action,
            )

            lan_url = f"http://{self.local_ip}:8787"
            messagebox.showinfo(
                "Installation Successful",
                f"Telegram Media Downloader is now installed and running in the background!\n\n"
                f"🌐 Local PC URL:  http://127.0.0.1:8787\n"
                f"📱 Other LAN Devices: {lan_url}\n\n"
                f"Auto-start is enabled. It will start silently whenever Windows starts.\n"
                f"Created by: Dipin a k",
            )
        else:
            self.status_lbl.config(text=f"❌ Error: {message}", fg="#ef4444")
            self.btn_cancel.config(state="normal")
            self.btn_install.config(state="normal", text="Retry")

    def finish_action(self) -> None:
        import webbrowser
        webbrowser.open("http://127.0.0.1:8787")
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    if "/S" in sys.argv or "/silent" in sys.argv or "--silent" in sys.argv:
        perform_installation(
            install_dir=default_install_dir(),
            auto_start=True,
            allow_lan_firewall=True,
            desktop_shortcut=True,
            start_menu_shortcut=True,
            launch_now=True,
            clean_data=("--clean" in sys.argv or "--reset" in sys.argv),
        )
    else:
        app = InstallerGUI()
        app.run()


if __name__ == "__main__":
    main()
