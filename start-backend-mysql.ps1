$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot "backend"
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$stdoutLog = Join-Path $backendPath "runserver.out.log"
$stderrLog = Join-Path $backendPath "runserver.err.log"

[Environment]::SetEnvironmentVariable("PATH", $null, "Process")

if (Test-Path $stdoutLog) { Remove-Item -LiteralPath $stdoutLog -Force }
if (Test-Path $stderrLog) { Remove-Item -LiteralPath $stderrLog -Force }

$env:DB_ENGINE = "mysql"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3307"
$env:DB_NAME = "wms"
$env:DB_USER = "root"
$env:DB_PASSWORD = "123456"

Start-Process `
  -FilePath $pythonExe `
  -ArgumentList "manage.py", "runserver", "127.0.0.1:8000", "--noreload" `
  -WorkingDirectory $backendPath `
  -RedirectStandardOutput $stdoutLog `
  -RedirectStandardError $stderrLog `
  -WindowStyle Hidden
