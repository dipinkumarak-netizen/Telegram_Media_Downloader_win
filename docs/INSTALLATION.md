# Installation Guide - Windows 11

Telegram Media Downloader is packaged as a standalone Windows installer and portable application.

## Quick Installation (Recommended)

1. Download **`TelegramMediaDownloader_Setup.exe`** from the `dist/` directory or GitHub Releases.
2. Double-click **`TelegramMediaDownloader_Setup.exe`**.
3. Click **Install Now ⚡**.

### What the installer does automatically:
- Installs the application to `%LOCALAPPDATA%\Programs\TelegramMediaDownloader`.
- Registers the application to auto-start silently in the background on Windows boot.
- Adds a Windows Firewall rule to allow port `8787` for Local Area Network (LAN) access.
- Creates Desktop and Start Menu shortcuts.
- Includes an uninstaller (`uninstall.exe`).

---

## Accessing the Dashboard

### On the Host PC:
Open your browser and navigate to:
```
http://127.0.0.1:8787
```

### From Other Computers / Phones on the same Wi-Fi / LAN:
Navigate to:
```
http://<HOST-PC-IP>:8787
```
*(Example: `http://192.168.1.6:8787`)*

---

## Configuration

1. In the Web Dashboard, click **⚙️ Settings** in the top right.
2. Enter your Telegram **API ID** and **API Hash** (obtain from https://my.telegram.org).
3. Log in with your phone number and OTP code.
4. Select the channels/groups you want to monitor and save.
5. Downloads will begin automatically in the background.

---

## Uninstallation

- Go to Windows Settings > **Installed Apps** > search for **Telegram Media Downloader** > **Uninstall**.
- Alternatively, launch `uninstall.exe` in the application directory.
