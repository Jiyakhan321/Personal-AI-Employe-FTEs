@echo off
REM Retry Playwright Chromium Installation
REM Run this when you have better network connectivity

echo ============================================================
echo Playwright Chromium Installation Retry
echo ============================================================
echo.
echo This script will download and install Playwright Chromium.
echo Please ensure you have:
echo   - At least 500 MB free on C: drive
echo   - Stable internet connection
echo   - 5-10 minutes for download
echo.
echo Press Ctrl+C to cancel, or wait for installation to complete...
echo.
echo ============================================================
echo.

REM Set download timeout to 15 minutes
set TIMEOUT=900

echo Starting download...
echo.

REM Install Chromium browser
python -m playwright install chromium

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Playwright Chromium installed successfully!
    echo ============================================================
    echo.
    echo You can now run LinkedIn Watcher:
    echo   cd AI_Employee_Vault\scripts
    echo   python linkedin_watcher.py --setup-session --vault ..
    echo.
) else (
    echo.
    echo ============================================================
    echo [FAILED] Installation failed. Try these steps:
    echo ============================================================
    echo.
    echo 1. Free up more space on C: drive (need 500+ MB)
    echo    del /q C:\Windows\Temp\*.*
    echo    del /q C:\Users\dell\AppData\Local\Temp\*.*
    echo.
    echo 2. Check your internet connection
    echo.
    echo 3. Try again later when network is better
    echo.
    echo 4. Or use Gmail Watcher instead (no download needed):
    echo    python gmail_watcher.py --authenticate --vault ..
    echo.
)

echo.
echo Press any key to exit...
pause >nul
