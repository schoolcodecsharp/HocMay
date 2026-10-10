param([ValidateRange(1, 65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Missing .venv. Create it and install requirements-lock.txt as described in README.md.'
}
Write-Host "California Housing Lab: http://127.0.0.1:$Port"
& $projectPython -m uvicorn app.main:app --host 127.0.0.1 --port $Port
exit $LASTEXITCODE
