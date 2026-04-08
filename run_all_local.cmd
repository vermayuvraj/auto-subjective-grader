@echo off
cd /d "%~dp0"

start "BTP Streamlit 8502" cmd /k "cd /d \"%~dp0\" && call run_streamlit_8502.cmd"
start "BTP API 8001" cmd /k "cd /d \"%~dp0\" && call run_api_8001.cmd"
start "BTP Web 3100" cmd /k "cd /d \"%~dp0web\" && set NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001 && npm run dev -- --hostname 127.0.0.1 --port 3100"

echo Starting project services...
echo Streamlit: http://127.0.0.1:8502
echo API: http://127.0.0.1:8001/api/health
echo Web: http://127.0.0.1:3100
