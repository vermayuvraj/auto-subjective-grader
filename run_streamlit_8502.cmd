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
"%~dp0.venv\Scripts\python.exe" -m streamlit run ".\src\app.py" --server.headless true --server.port 8502
