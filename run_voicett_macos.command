#!/bin/bash

VENV_DIR=.venv
PYTHON_EXE=python3
SCRIPT_NAME=voicett_live.py

# Перевірка наявності віртуального середовища
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_EXE -m venv $VENV_DIR
fi

# Активація віртуального середовища
source $VENV_DIR/bin/activate

# Перевірка та встановлення залежностей
if [ -f "requirements.txt" ]; then
    echo "Checking and installing dependencies..."
    pip install -r requirements.txt
fi

# Запуск скрипта
echo "Starting VoiceTT-Live..."
python $SCRIPT_NAME