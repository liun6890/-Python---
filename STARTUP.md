# Startup

Use `start-dev.ps1` as the default startup entry for this WMS project.

It starts:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`
- Database: MySQL `127.0.0.1:3307`, database `wms`, user `root`, password `123456`

Notes:

- Do not start the backend with the default SQLite configuration for this project.
- The frontend is synced into `C:\Users\Administrator\PycharmProjects\Pythonlearn\wl_frontend_run` before Vite starts. This avoids Vite/esbuild path issues caused by the original Chinese project path and the `wl_ascii` junction.
- The script stops existing Django/Vite listeners on ports `8000` and `5173` before starting fresh services.

Command:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\Administrator\PycharmProjects\Pythonlearn\学习实验系统\wl\start-dev.ps1"
```
