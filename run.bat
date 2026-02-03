@echo off
setlocal enabledelayedexpansion

set TYPE=local
set TAG=paco:latest
set CLEAN=false
set IS_DOCKER=false
set IS_LOCAL=false

set RUN=false

:parse
if "%~1"=="" goto endparse
if "%~1"=="--docker" (
    set TYPE=docker
    set IS_DOCKER=true
    shift
    goto parse
)
if "%~1"=="--local" (
    set TYPE=local
    set IS_LOCAL=true
    shift
    goto parse
)
if "%~1"=="--clean" (
    set CLEAN=true
    shift
    goto parse
)
if "%~1"=="--help" goto usage
shift
goto parse

:endparse

if "%IS_DOCKER%"=="true" if "%IS_LOCAL%"=="true" (
    echo Error: --local and --docker cannot be used together.
    goto usage
)

if "%CLEAN%"=="true" (
    echo Cleaning temporary files...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    echo Cleanup complete.
)

if "%TYPE%"=="local" goto local
if "%TYPE%"=="docker" goto docker
echo Invalid build type: %TYPE%
goto usage

:local
echo Installing Python dependencies...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip not found. Please install Python and pip.
    exit /b 1
)

pip install -r requirements.txt
if exist "gui/requirements.txt" pip install -r gui/requirements.txt
if exist "simulator/requirements.txt" pip install -r simulator/requirements.txt
echo Local setup complete. Starting application...
python src --gui
goto end

:docker
echo Building Docker image: %TAG%
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: docker not found. Please install Docker.
    exit /b 1
)

docker build -t %TAG% .
if %errorlevel% neq 0 (
    echo Docker build failed.
    exit /b 1
)
echo Docker build successful. Starting application...
docker run -p 8000:8000 -p 8050:8050 -p 8888:8888 -p 8001:8001 -it %TAG%
goto end

:usage
echo PACO Run Script
echo Usage: run.bat [OPTIONS]
echo Options:
echo   --docker                Use Docker mode (builds & runs image)
echo   --local                 Use Local mode (installs deps & runs) [Default]
echo   --clean                 Clean __pycache__ directories
echo   --help                  Show this help
goto end

:end
endlocal
