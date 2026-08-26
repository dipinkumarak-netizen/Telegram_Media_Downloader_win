# ⚡ Telegram Media Downloader — Windows 11

**Telegram Media Downloader for Windows 11** is a high-performance, background media downloader for Telegram channels, groups, and chats. It runs completely in the background without any command prompt window, starts automatically on Windows boot, and provides a modern web interface accessible from both the local PC and any device across your Local Area Network (LAN / Wi-Fi).

---

## 🌟 Features / പ്രധാന സവിശേഷതകൾ

- **📦 Standalone Windows Setup Installer (.exe)**:
  - Single-click graphical installer (`TelegramMediaDownloader_Setup.exe`) that installs the app, registers Windows auto-start, configures Windows Firewall, and creates shortcuts.
- **🔕 Silent Background Mode (Windowless)**:
  - Runs silently as a background service without opening black console or command prompt windows (`--noconsole`).
- **🚀 Auto-Start on Boot**:
  - Automatically starts downloading whenever Windows boots up or logs in.
- **🌐 Remote LAN / Wi-Fi Access (`0.0.0.0:8787`)**:
  - Access the web dashboard from any PC, laptop, or mobile phone on the same Wi-Fi network at `http://<WINDOWS-IP>:8787` (e.g. `http://192.168.1.6:8787`).
- **📊 Direct Dashboard & Single-Page Settings**:
  - Opens straight to the Live Download Dashboard.
  - All configurations (API credentials, Phone & OTP login, Channel selection, Storage paths, Concurrency, Speed limits, Jellyfin integration, Password protection) in a single unified settings page (`⚙️ Settings`).
- **🎬 Automated Media Organization & Jellyfin Integration**:
  - Categorizes downloads into `movies/`, `tv/`, `music/`, `documents/`, and `other/`.
  - Automatically triggers Jellyfin library scan upon download completion.

---

## 📥 Installation / എങ്ങനെ ഇൻസ്റ്റാൾ ചെയ്യാം?

### Option 1: Using the Windows Installer (Recommended)
1. Download **[`dist/TelegramMediaDownloader_Setup.exe`](dist/TelegramMediaDownloader_Setup.exe)**.
2. Double-click **`TelegramMediaDownloader_Setup.exe`**.
3. Click **Install Now ⚡**.
4. The application will be installed into `%LOCALAPPDATA%\Programs\TelegramMediaDownloader` and will start in the background immediately.

### Option 2: Portable Executable (No Installation)
- Double-click **[`dist/TelegramMediaDownloader.exe`](dist/TelegramMediaDownloader.exe)** to run directly.

---

## 🌐 Accessing the Web Dashboard

| Location | URL |
| :--- | :--- |
| **Host PC** | `http://127.0.0.1:8787` or `http://localhost:8787` |
| **Other Devices on LAN / Wi-Fi** | `http://<YOUR-PC-IP>:8787` *(e.g. `http://192.168.1.6:8787`)* |

*Note: The exact LAN URL is prominently displayed at the top of the dashboard with a one-click copy button.*

---

## ⚙️ Quick Configuration Guide

1. Open `http://127.0.0.1:8787` (or your LAN IP from another device).
2. Click **⚙️ Settings** in the top navigation bar.
3. **Step 1 — Telegram API**: Enter your `API ID` and `API Hash` from [my.telegram.org](https://my.telegram.org) and click **Save Telegram API**.
4. **Step 2 — Telegram Login**: Enter your phone number with country code (e.g. `+919876543210`), click **Send Code**, and enter the OTP code received on Telegram.
5. **Step 3 — Channels & Groups**: Search and select the channels/groups you wish to download from, then click **Save Monitored Sources**.
6. **Step 4 — Storage & Preferences**: Adjust download folders, concurrency (1-16), speed limits, and Jellyfin server URL if desired.
7. Any new files posted in your selected channels will automatically download to your computer!

---

## 🛠️ Building From Source

To build the standalone `.exe` binaries yourself on Windows:

```powershell
# 1. Install dependencies
pip install -r requirements.lock pyinstaller

# 2. Build executables (creates TelegramMediaDownloader.exe and TelegramMediaDownloader_Setup.exe in dist/)
python build_exe.py
```
Or simply double-click `build.bat`.

---

## 🗑️ Uninstallation

- Go to **Windows Settings > Apps > Installed Apps > Telegram Media Downloader > Uninstall**.
- Or run `uninstall.exe` in `%LOCALAPPDATA%\Programs\TelegramMediaDownloader`.
- Your downloaded media files remain completely safe in your Downloads folder.

---

## 📄 License
MIT License
