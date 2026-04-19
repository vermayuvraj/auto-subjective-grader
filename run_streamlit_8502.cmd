@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0src;%PYTHONPATH%
"%~dp0.venv\Scripts\python.exe" -m streamlit run ".\src\app.py" --server.headless true --server.port 8502
