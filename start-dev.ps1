$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectLeaf = Split-Path -Leaf $projectRoot

if ($projectLeaf -eq "wl_ascii") {
  $workspaceRoot = Split-Path -Parent $projectRoot
} else {
  $workspaceRoot = Split-Path -Parent (Split-Path -Parent $projectRoot)
}

$asciiProjectRoot = Join-Path $workspaceRoot "wl_ascii"
$runtimeProjectRoot = if (Test-Path $asciiProjectRoot) { $asciiProjectRoot } else { $projectRoot }

$backendPath = Join-Path $runtimeProjectRoot "backend"
$frontendSourcePath = Join-Path $runtimeProjectRoot "frontend"
$frontendRunPath = Join-Path $workspaceRoot "wl_frontend_run"
$pythonExe = Join-Path $runtimeProjectRoot ".venv\Scripts\python.exe"
$nodeExe = (Get-Command "node.exe" -ErrorAction SilentlyContinue).Source

if (-not (Test-Path $pythonExe)) {
  throw "Python venv not found: $pythonExe"
}

if (-not $nodeExe -and (Test-Path "C:\Program Files\nodejs\node.exe")) {
  $nodeExe = "C:\Program Files\nodejs\node.exe"
}

if (-not $nodeExe) {
  throw "node.exe not found. Install Node.js or add node.exe to PATH."
}

function Get-ListenerPids {
  param([int]$Port)

  $lines = netstat -ano | Select-String "LISTENING"
  foreach ($line in $lines) {
    $parts = ($line.Line.Trim() -split "\s+")
    if ($parts.Count -ge 5 -and $parts[1] -match ":$Port$") {
      [int]$parts[-1]
    }
  }
}

function Stop-ExpectedListener {
  param(
    [int]$Port,
    [string]$ExpectedPattern
  )

  $pids = @(Get-ListenerPids -Port $Port | Sort-Object -Unique)
  foreach ($processId in $pids) {
    $proc = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
    $commandLine = if ($proc) { $proc.CommandLine } else { "" }
    if ($commandLine -match $ExpectedPattern) {
      Stop-Process -Id $processId -Force
      Write-Host "Stopped existing service on port $Port (PID $processId)."
    } else {
      throw "Port $Port is already used by PID ${processId}: $commandLine"
    }
  }
}

Stop-ExpectedListener -Port 8000 -ExpectedPattern "manage\.py|runserver"
Stop-ExpectedListener -Port 5173 -ExpectedPattern "vite|node"

if (-not (Test-Path $frontendRunPath)) {
  New-Item -ItemType Directory -Path $frontendRunPath | Out-Null
}

robocopy $frontendSourcePath $frontendRunPath /E /XD node_modules dist .vscode /XF vite.current.out.log vite.current.err.log vite.out.log vite.err.log | Out-Host
if ($LASTEXITCODE -ge 8) {
  throw "Failed to sync frontend runtime directory. Robocopy exit code: $LASTEXITCODE"
}

$sourceNodeModules = Join-Path $frontendSourcePath "node_modules"
$runNodeModules = Join-Path $frontendRunPath "node_modules"
if (-not (Test-Path $sourceNodeModules)) {
  throw "node_modules not found: $sourceNodeModules"
}

if (-not (Test-Path $runNodeModules)) {
  New-Item -ItemType Junction -Path $runNodeModules -Target $sourceNodeModules | Out-Null
}

$viteBin = Join-Path $frontendRunPath "node_modules\vite\bin\vite.js"
if (-not (Test-Path $viteBin)) {
  throw "Vite entry not found: $viteBin"
}

$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$combinedPath = @(($machinePath, $userPath) | Where-Object { $_ }) -join ";"
if ($combinedPath) {
  [Environment]::SetEnvironmentVariable("Path", $combinedPath, "Process")
}
[Environment]::SetEnvironmentVariable("PATH", $null, "Process")

$env:DB_ENGINE = "mysql"
$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "3307"
$env:DB_NAME = "wms"
$env:DB_USER = "root"
$env:DB_PASSWORD = "123456"

$backendOut = Join-Path $backendPath "runserver.current.out.log"
$backendErr = Join-Path $backendPath "runserver.current.err.log"
$frontendOut = Join-Path $frontendRunPath "vite.current.out.log"
$frontendErr = Join-Path $frontendRunPath "vite.current.err.log"

Start-Process `
  -FilePath $pythonExe `
  -ArgumentList "manage.py", "runserver", "127.0.0.1:8000", "--noreload" `
  -WorkingDirectory $backendPath `
  -RedirectStandardOutput $backendOut `
  -RedirectStandardError $backendErr `
  -WindowStyle Hidden

Start-Process `
  -FilePath $nodeExe `
  -ArgumentList $viteBin, "--host", "127.0.0.1" `
  -WorkingDirectory $frontendRunPath `
  -RedirectStandardOutput $frontendOut `
  -RedirectStandardError $frontendErr `
  -WindowStyle Hidden

Start-Sleep -Seconds 6

$backendStatus = try {
  (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000" -TimeoutSec 5).StatusCode
} catch {
  "ERROR: $($_.Exception.Message)"
}

$frontendStatus = try {
  (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:5173" -TimeoutSec 5).StatusCode
} catch {
  "ERROR: $($_.Exception.Message)"
}

Write-Host "Backend:  http://127.0.0.1:8000  Status=$backendStatus"
Write-Host "Frontend: http://127.0.0.1:5173  Status=$frontendStatus"
Write-Host "Database: mysql://root:123456@127.0.0.1:3307/wms"
Write-Host "Frontend runtime directory: $frontendRunPath"
