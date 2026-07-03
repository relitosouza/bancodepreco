@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%
echo Iniciando o servidor do Banco de Precos PNCP...
python app/main.py
if %errorlevel% neq 0 (
    echo.
    echo Ocorreu um erro ao tentar iniciar o servidor.
    pause
)
