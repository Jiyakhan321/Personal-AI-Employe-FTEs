@echo off
REM AI Employee - Complete Silver Tier Startup
REM Opens all watchers and auto-poster in separate windows

echo ============================================================
echo AI Employee - Silver Tier Startup
echo ============================================================
echo.

cd /d "%~dp0"

REM Window 1: Gmail Watcher
echo Starting Gmail Watcher...
start "Gmail Watcher" python gmail_watcher.py --vault .. --continuous --interval 120
timeout /t 2 /nobreak >nul

REM Window 2: LinkedIn Watcher
echo Starting LinkedIn Watcher...
start "LinkedIn Watcher" python linkedin_watcher.py --vault .. --continuous --interval 300
timeout /t 2 /nobreak >nul

REM Window 3: Orchestrator
echo Starting Orchestrator...
start "Orchestrator" python orchestrator.py .. --continuous --interval 60
timeout /t 2 /nobreak >nul

REM Window 4: LinkedIn Auto-Poster
echo Starting LinkedIn Auto-Poster...
start "LinkedIn Auto-Poster" python linkedin_auto_poster.py --vault .. --continuous --interval 60

echo.
echo ============================================================
echo All services started!
echo ============================================================
echo.
echo Running:
echo   - Gmail Watcher (every 2 min)
echo   - LinkedIn Watcher (every 5 min)
echo   - Orchestrator (every 60 sec)
echo   - LinkedIn Auto-Poster (every 60 sec)
echo.
echo To stop: Close each window or press Ctrl+C
echo ============================================================
echo.
pause
