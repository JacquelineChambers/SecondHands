param(
    [string]$BridgeDirectory = (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Documents/Femto-Bolt-Depth-Test-2026-10-17/bridge'),
    [int]$MaxFrames = 54000,
    [ValidateSet('mediapipe', 'executorch-qnn')]
    [string]$GestureBackend = 'mediapipe'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$projectPython = Join-Path $projectRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Install the project vision environment before starting the preview.'
}
if (-not (Test-Path -LiteralPath (Join-Path $BridgeDirectory 'direct_capture.py'))) {
    throw 'Pass -BridgeDirectory with the installed Femto Bolt bridge directory.'
}
Push-Location $projectRoot
try {
    & $projectPython -m secondhands.recognition camera --camera-source orbbec --orbbec-bridge $BridgeDirectory --max-frames $MaxFrames --gesture-backend $GestureBackend --preview --quiet
    if ($LASTEXITCODE -ne 0) { throw "Orbbec preview exited with code $LASTEXITCODE" }
} finally {
    Pop-Location
}
