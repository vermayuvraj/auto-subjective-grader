@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0src;%PYTHONPATH%
for /f "delims=" %%i in ('gcloud config get-value project 2^>nul') do (
  if not "%%i"=="(unset)" set GOOGLE_CLOUD_PROJECT=%%i
)
if not defined GOOGLE_CLOUD_LOCATION set GOOGLE_CLOUD_LOCATION=global
"%~dp0.venv\Scripts\python.exe" -m uvicorn backend_api.main:app --host 127.0.0.1 --port 8001
