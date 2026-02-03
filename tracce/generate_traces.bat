@echo off
REM Script per generare tutte le tracce da un file BPMN
REM Uso: generate_traces.bat [file_bpmn.json]

echo ========================================
echo Generatore di Tracce BPMN
echo ========================================
echo.

REM Verifica argomenti
if "%1"=="" (
    echo Errore: Specificare un file BPMN
    echo Uso: generate_traces.bat file_bpmn.json
    echo.
    echo Esempio: generate_traces.bat bpmn_fig8_bound_135_15.json
    exit /b 1
)

REM Verifica se il file esiste
if not exist "%1" (
    echo Errore: File %1 non trovato
    exit /b 1
)

REM Ottieni il nome base del file senza estensione
for %%F in ("%1") do set "basename=%%~nF"

echo File BPMN: %1
echo Output tracce: %basename%_traces.json
echo Output albero: %basename%_execution_tree.json
echo.

REM Genera le tracce
python generate_all_traces.py "%1" ^
    -o "%basename%_traces.json" ^
    --execution-tree-output "%basename%_execution_tree.json"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Completato con successo!
    echo ========================================
    echo.
    echo File generati:
    echo   - %basename%_traces.json
    echo   - %basename%_execution_tree.json
    echo.
    echo Per analizzare le tracce:
    echo   python analyze_traces.py %basename%_traces.json
) else (
    echo.
    echo ========================================
    echo Errore durante la generazione
    echo ========================================
    echo.
    echo Verifica che:
    echo   1. Il simulatore sia in esecuzione: cd simulator ^&^& python src/main.py
    echo   2. Il server PACO sia in esecuzione: python -m src.server
    exit /b 1
)
