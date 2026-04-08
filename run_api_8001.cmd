@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0.venv\Lib\site-packages;%~dp0src;%PYTHONPATH%
"C:\Users\Yuvraj Verma\AppData\Local\Programs\Python\Python310\python.exe" -m uvicorn backend_api.main:app --host 127.0.0.1 --port 8001
