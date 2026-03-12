@echo off
REM OpenClaw Browser Relay Server Startup Script for Windows
REM Port: 9997

echo.
echo ============================================================
echo OpenClaw Browser Relay Server
echo ============================================================
echo Listening on: ws://localhost:9997
echo ============================================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "SERVER_DIR=%SCRIPT_DIR%server"

echo Changing to server directory: %SERVER_DIR%
cd /d "%SERVER_DIR%"

echo Starting server...
python server.py

pause
