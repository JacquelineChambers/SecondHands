param([string]$WorkDirectory = '')

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$root = if ($WorkDirectory) { [IO.Path]::GetFullPath($WorkDirectory) } else { Join-Path $projectRoot 'artifacts/qnn' }
$generatedSource = Join-Path $root 'stream-src'
New-Item -ItemType Directory -Force -Path $generatedSource | Out-Null
Copy-Item -LiteralPath "$PSScriptRoot/CMakeLists.txt" -Destination "$generatedSource/CMakeLists.txt"
Copy-Item -LiteralPath "$PSScriptRoot/qnn_stream.cpp" -Destination "$generatedSource/qnn_stream.cpp"

# Enable the native Windows Python binding in the pinned ExecuTorch checkout.
$qnnCmake = Join-Path $root 'executorch/backends/qualcomm/CMakeLists.txt'
$qnnText = [IO.File]::ReadAllText($qnnCmake).Replace("`r`n", "`n")
$originalGuard = 'if(${CMAKE_SYSTEM_PROCESSOR} MATCHES "x86_64|AMD64")'
$nativeGuard = 'if(${CMAKE_SYSTEM_PROCESSOR} MATCHES "x86_64|AMD64" OR' + "`n" + '   (WIN32 AND CMAKE_SYSTEM_PROCESSOR MATCHES "ARM64|aarch64"))'
if ($qnnText.Contains($originalGuard)) {
    [IO.File]::WriteAllText($qnnCmake, $qnnText.Replace($originalGuard, $nativeGuard))
} elseif (-not $qnnText.Contains($nativeGuard)) {
    throw 'Unexpected Qualcomm CMake source; use the documented ExecuTorch revision.'
}
$msvc = (Get-ChildItem -LiteralPath "$root/toolchain/msvc/VC/Tools/MSVC" -Directory | Select-Object -Last 1).FullName
$kit = "$root/toolchain/msvc/Windows Kits/10"
$sdkVersion = (Get-ChildItem -LiteralPath "$kit/Include" -Directory | Select-Object -Last 1).Name
$env:PATH = "$msvc/bin/Hostarm64/arm64;$kit/bin/$sdkVersion/arm64;$root/../venvs/qnn-export/Scripts;$env:PATH"
$env:INCLUDE = "$msvc/include;$kit/Include/$sdkVersion/ucrt;$kit/Include/$sdkVersion/shared;$kit/Include/$sdkVersion/um;$kit/Include/$sdkVersion/winrt"
$env:LIB = "$msvc/lib/arm64;$kit/Lib/$sdkVersion/ucrt/arm64;$kit/Lib/$sdkVersion/um/arm64"
$env:VCToolsInstallDir = "$msvc/"
$env:VSCMD_ARG_HOST_ARCH = 'arm64'
$env:VSCMD_ARG_TGT_ARCH = 'arm64'
$qnnHeader = Get-ChildItem -LiteralPath "$root/qairt" -Recurse -Filter QnnInterface.h | Select-Object -First 1
if (-not $qnnHeader) { throw 'Extracted QNN headers not found' }
$qnnSdk = $qnnHeader.Directory.Parent.Parent.FullName
$env:QNN_SDK_ROOT = $qnnSdk
$pythonDev = "$root/python-devel/tools"
$configureArgs = @(
    '-S', "$root/stream-src", '-B', "$root/build-stream", '-G', 'Ninja',
    '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_SYSTEM_NAME=Windows', '-DCMAKE_SYSTEM_PROCESSOR=ARM64',
    "-DQNN_SDK_ROOT=$qnnSdk", "-DPYTHON_EXECUTABLE=$root/python-arm64/python.exe",
    "-DPYTHON_INCLUDE_DIR=$pythonDev/include", "-DPYTHON_LIBRARY=$pythonDev/libs/python312.lib",
    "-DPython3_EXECUTABLE=$root/python-arm64/python.exe", "-DPython3_INCLUDE_DIR=$pythonDev/include",
    "-DPython3_LIBRARY=$pythonDev/libs/python312.lib", '-DPYBIND11_FINDPYTHON=ON'
    "-DPython_EXECUTABLE=$root/python-arm64/python.exe", "-DPython_INCLUDE_DIR=$pythonDev/include",
    "-DPython_LIBRARY=$pythonDev/libs/python312.lib",
    "-DFLATC_EXECUTABLE=$root/aot-python/executorch/data/bin/flatc.exe"
)
$ErrorActionPreference = 'Continue'
& cmake @configureArgs
if ($LASTEXITCODE) { exit $LASTEXITCODE }
& cmake --build "$root/build-stream" --target secondhands_qnn_stream PyQnnManagerAdaptor --parallel 6
if ($LASTEXITCODE) { exit $LASTEXITCODE }
$ErrorActionPreference = 'Stop'
Copy-Item -LiteralPath "$root/build-stream/executorch-runtime/backends/qualcomm/PyQnnManagerAdaptor.pyd" -Destination "$root/aot-python/executorch/backends/qualcomm/python/PyQnnManagerAdaptor.cp312-win_arm64.pyd"
Get-ChildItem -LiteralPath "$qnnSdk/lib/aarch64-windows-msvc" -Filter '*.dll' | Copy-Item -Destination "$root/build-stream"
# The ARM64 Microsoft runtime was downloaded and checked against its VS catalog hash.
Get-ChildItem -LiteralPath "$root/runtime" -Filter '*.dll' | Where-Object { $_.Name -match '^(msvc|vcruntime|concrt|vccorlib)' } | Copy-Item -Destination "$root/build-stream"
