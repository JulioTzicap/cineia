$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location (Join-Path $ProjectRoot 'backend')
try { & '.\.venv\Scripts\python.exe' -m pytest -q } finally { Pop-Location }
Push-Location (Join-Path $ProjectRoot 'frontend')
try { npm run build } finally { Pop-Location }
