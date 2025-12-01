@echo off
title ROBO DE MONITORAMENTO
color 0A
echo ==========================================
echo   INICIANDO ROBO... (Pode fechar o VS Code)
echo ==========================================
echo.
cd /d "%~dp0"
python Monitoramento_Frota.py
echo.
echo O robo parou ou deu erro.
pause