@echo off
title IoT Asset Tracking - Servidor
cd /d "%~dp0"
echo ============================================================
echo   Iniciando Plataforma de Rastreio de Ativos (IoT + GPS)
echo ============================================================
echo.
echo URL do Painel: http://127.0.0.1:8000
echo Swagger API:   http://127.0.0.1:8000/docs
echo.
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe app.py
) else (
    python app.py
)
pause

