$ErrorActionPreference = "Stop"
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Python do .venv não encontrado em $python"
}
& $python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
& $python (Join-Path $PSScriptRoot "app.py")
