@echo off
REM LinkedIn Auto-Post - Quick Post Command
REM Posts all approved content to LinkedIn

cd /d "%~dp0"

echo ================================================================
echo LinkedIn Auto-Post
echo ================================================================
echo.

python linkedin_auto_poster.py --vault .. --post-approved

echo.
echo ================================================================
echo Done. Check Logs/ folder for details.
echo ================================================================
pause
