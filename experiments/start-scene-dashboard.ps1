param(
    [string]$BridgeDirectory = (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Documents/Femto-Bolt-Depth-Test-2026-10-17/bridge'),
    [string]$ObjectModel = '',
    [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
$logDirectory = Join-Path $projectRoot 'artifacts/scene-understanding'
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Prepare the project vision and dashboard environment first.' }
if (-not (Test-Path -LiteralPath (Join-Path $BridgeDirectory 'direct_capture.py'))) { throw 'Pass -BridgeDirectory with the installed Orbbec bridge.' }
$env:SECONDHANDS_ORBBEC_BRIDGE = $BridgeDirectory
if ($ObjectModel) { $env:SECONDHANDS_OBJECT_MODEL = $ObjectModel }

function Read-LocalJson([string]$Uri) {
    try { Invoke-RestMethod -Uri $Uri -TimeoutSec 2 } catch { $null }
}

$startedProcesses = @()
$health = Read-LocalJson 'http://127.0.0.1:8765/api/health'
if ($health -and -not $health.scene_understanding) {
    throw 'An older API is using port 8765. Stop that API and run this launcher again.'
}
if (-not $health) {
    $apiProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m','secondhands.api') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'api.stdout.log') -RedirectStandardError (Join-Path $logDirectory 'api.stderr.log') -PassThru
    $startedProcesses += [pscustomobject]@{ Role = 'API'; Id = $apiProcess.Id }
}

$modelHealth = Read-LocalJson 'http://127.0.0.1:8009/v1/models'
if (-not $modelHealth) {
    $modelPython = Join-Path $projectRoot 'artifacts/qnn/python-arm64/python.exe'
    $modelLauncher = Join-Path $projectRoot 'artifacts/jevvision-run/launch.py'
    if ((Test-Path -LiteralPath $modelPython) -and (Test-Path -LiteralPath $modelLauncher)) {
        $modelProcess = Start-Process -FilePath $modelPython -ArgumentList @('-u','-B',('"' + $modelLauncher + '"')) -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'jevvision.stdout.log') -RedirectStandardError (Join-Path $logDirectory 'jevvision.stderr.log') -PassThru
        $startedProcesses += [pscustomobject]@{ Role = 'JEVision'; Id = $modelProcess.Id }
    } else {
        Write-Warning 'JEVision is not prepared. Tracking and object detection can still run with scene analysis disabled.'
    }
}

$uiRunning = $false
try { $uiRunning = (Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 } catch {}
if (-not $uiRunning) {
    $vitePath = Join-Path $projectRoot 'ui/node_modules/vite/bin/vite.js'
    if (-not (Test-Path -LiteralPath $vitePath)) { throw 'Install the UI dependencies before starting the dashboard.' }
    $bunCommand = Get-Command bun -ErrorAction SilentlyContinue
    $runtimePath = if ($bunCommand) { $bunCommand.Source } else { (Get-Command node -ErrorAction Stop).Source }
    $uiProcess = Start-Process -FilePath $runtimePath -ArgumentList @(('"' + $vitePath + '"')) -WorkingDirectory (Join-Path $projectRoot 'ui') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'ui.stdout.log') -RedirectStandardError (Join-Path $logDirectory 'ui.stderr.log') -PassThru
    $startedProcesses += [pscustomobject]@{ Role = 'UI'; Id = $uiProcess.Id }
}

$startedProcesses | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $logDirectory 'started-processes.json') -Encoding utf8
$deadline = (Get-Date).AddSeconds(20)
do {
    $health = Read-LocalJson 'http://127.0.0.1:8765/api/health'
    try { $uiRunning = (Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 } catch { $uiRunning = $false }
    if ($health.scene_understanding -and $uiRunning) { break }
    Start-Sleep -Milliseconds 500
} while ((Get-Date) -lt $deadline)
if (-not $health.scene_understanding -or -not $uiRunning) { throw 'Startup failed. Inspect artifacts/scene-understanding service logs.' }
Write-Output 'Scene dashboard ready: http://127.0.0.1:5173'
if ($OpenBrowser) { Start-Process 'http://127.0.0.1:5173' }
