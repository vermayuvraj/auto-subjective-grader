@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0src;%PYTHONPATH%
"%~dp0.venv\Scripts\python.exe" -m uvicorn backend_api.main:app --host 127.0.0.1 --port 8001
