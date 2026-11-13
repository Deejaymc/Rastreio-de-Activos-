Set-Location -Path $PSScriptRoot
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Iniciando Servidor IoT Asset Tracking" -ForegroundColor Cyan
Write-Host "  Painel:  http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  Swagger: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\app.py"

