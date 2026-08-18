@echo off
start "backend" cmd /k "cd /d %~dp0backend && python manage.py runserver 0.0.0.0:8000"
start "frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
