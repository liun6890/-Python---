@echo off
set DB_ENGINE=mysql
set DB_HOST=127.0.0.1
set DB_PORT=3307
set DB_NAME=wms
set DB_USER=root
set DB_PASSWORD=123456

cd /d "%~dp0backend"
"%~dp0.venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
