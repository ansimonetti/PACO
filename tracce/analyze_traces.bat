@echo off
REM Script per analizzare le tracce generate
REM Uso: analyze_traces.bat [file_traces.json]

echo ========================================
echo Analizzatore di Tracce BPMN
echo ========================================
echo.

REM Verifica argomenti
if "%1"=="" (
    echo Errore: Specificare un file di tracce
    echo Uso: analyze_traces.bat file_traces.json
    echo.
    echo Esempio: analyze_traces.bat bpmn_fig8_traces.json
    exit /b 1
)

REM Verifica se il file esiste
if not exist "%1" (
    echo Errore: File %1 non trovato
    exit /b 1
)

REM Ottieni il nome base del file senza estensione
for %%F in ("%1") do set "basename=%%~nF"

echo File tracce: %1
echo Output CSV: %basename%_summary.csv
echo.

REM Analizza le tracce
python analyze_traces.py "%1" --export-csv "%basename%_summary.csv"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Analisi completata!
    echo ========================================
    echo.
    echo File CSV generato: %basename%_summary.csv
) else (
    echo.
    echo ========================================
    echo Errore durante l'analisi
    echo ========================================
    exit /b 1
)
