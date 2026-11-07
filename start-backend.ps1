$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPath = Join-Path $ProjectRoot 'backend'
$PythonPath = Join-Path $BackendPath '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $PythonPath)) { throw 'No existe backend/.venv. Instala primero las dependencias del README.' }
Set-Location -LiteralPath $BackendPath
& $PythonPath -m uvicorn app.main:app --reload --port 8000
