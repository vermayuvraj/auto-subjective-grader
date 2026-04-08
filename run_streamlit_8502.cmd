@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0.venv\Lib\site-packages;%~dp0src;%PYTHONPATH%
"C:\Users\Yuvraj Verma\AppData\Local\Programs\Python\Python310\python.exe" -m streamlit run ".\src\app.py" --server.headless true --server.port 8502
