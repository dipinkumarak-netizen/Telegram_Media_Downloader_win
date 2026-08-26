@echo off
:: Batch script to add Windows Firewall rule for Telegram Media Downloader
title Telegram Media Downloader - Firewall Configurator
echo ======================================================================
echo   Configuring Windows Firewall for Telegram Media Downloader
echo   Opening TCP Port 8787 for Local Area Network (LAN) Access
echo ======================================================================

netsh advfirewall firewall add rule name="Telegram Media Downloader" dir=in action=allow protocol=TCP localport=8787 profile=any

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Port 8787 has been successfully opened!
    echo Other devices on your Wi-Fi/LAN can now access the web dashboard.
    echo.
) else (
    echo.
    echo [NOTE] If you saw an access error above, please right-click this 
    echo file and choose "Run as administrator".
    echo.
)
pause
