@echo off
setlocal enabledelayedexpansion

set VENV_DIR=.venv
set PYTHON_EXE=python
set SCRIPT_NAME=voicett_live.py

:: Перевірка наявності віртуального середовища
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    %PYTHON_EXE% -m venv %VENV_DIR%
)

:: Активація віртуального середовища
call %VENV_DIR%\Scripts\activate

:: Перевірка та встановлення залежностей
if exist requirements.txt (
    echo Checking and installing dependencies...
    pip install -r requirements.txt
)

:: Запуск скрипта
echo Starting VoiceTT-Live...
python %SCRIPT_NAME%

pause