@echo off
setlocal
set SCRIPT_DIR=%~dp0
set PYTHONPATH=%PYTHONPATH%;%SCRIPT_DIR%src
python src\run_benchmark.py
