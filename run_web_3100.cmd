@echo off
cd /d "%~dp0\web"
set NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001
call npm run dev -- --hostname 127.0.0.1 --port 3100
