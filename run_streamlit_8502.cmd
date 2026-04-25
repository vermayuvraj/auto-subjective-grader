@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0src;%PYTHONPATH%
if not defined GOOGLE_APPLICATION_CREDENTIALS (
  if exist "%APPDATA%\gcloud\application_default_credentials.json" (
    set "GOOGLE_APPLICATION_CREDENTIALS=%APPDATA%\gcloud\application_default_credentials.json"
  )
)
if not defined GOOGLE_APPLICATION_CREDENTIALS (
  for /f "delims=" %%i in ('gcloud config get-value account 2^>nul') do (
    if not "%%i"=="(unset)" (
      if exist "%APPDATA%\gcloud\legacy_credentials\%%i\adc.json" (
        set "GOOGLE_APPLICATION_CREDENTIALS=%APPDATA%\gcloud\legacy_credentials\%%i\adc.json"
      )
    )
  )
)
for /f "delims=" %%i in ('gcloud config get-value project 2^>nul') do (
  if not "%%i"=="(unset)" set GOOGLE_CLOUD_PROJECT=%%i
)
if not defined GOOGLE_CLOUD_LOCATION set GOOGLE_CLOUD_LOCATION=global
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" --version >nul 2>&1
  if errorlevel 1 set "PYTHON_EXE="
) else (
  set "PYTHON_EXE="
)
if not defined PYTHON_EXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python310\python.exe"
if not defined PYTHON_EXE set "PYTHON_EXE=python"
"%PYTHON_EXE%" -m streamlit run ".\src\app.py" --server.headless true --server.port 8502
