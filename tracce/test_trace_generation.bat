@echo off
REM Test rapido del sistema di generazione tracce

echo ========================================
echo TEST SISTEMA GENERAZIONE TRACCE
echo ========================================
echo.

echo [1/4] Verifica file necessari...
if not exist "generate_all_traces.py" (
    echo ERRORE: generate_all_traces.py non trovato
    exit /b 1
)
if not exist "analyze_traces.py" (
    echo ERRORE: analyze_traces.py non trovato
    exit /b 1
)
if not exist "simple_test_model.json" (
    echo ERRORE: simple_test_model.json non trovato
    exit /b 1
)
echo OK - Tutti i file necessari sono presenti
echo.

echo [2/4] Verifica server in esecuzione...
echo (Assicurati che i server siano avviati in altri terminali)
echo   - Simulatore: cd simulator ^&^& python src/main.py
echo   - PACO: python -m src.server
echo.
timeout /t 3 >nul

echo [3/4] Genera tracce dal modello di test...
python generate_all_traces.py simple_test_model.json ^
    -o test_traces.json ^
    --execution-tree-output test_execution_tree.json ^
    --max-nodes 100

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRORE: Generazione tracce fallita!
    echo.
    echo Verifica che:
    echo   1. I server siano in esecuzione
    echo   2. Le porte 8000 e 8001 siano disponibili
    echo   3. Python e le dipendenze siano installate
    exit /b 1
)

echo.
echo [4/4] Analizza le tracce generate...
python analyze_traces.py test_traces.json --export-csv test_summary.csv

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRORE: Analisi tracce fallita!
    exit /b 1
)

echo.
echo ========================================
echo TEST COMPLETATO CON SUCCESSO!
echo ========================================
echo.
echo File generati:
echo   - test_traces.json
echo   - test_execution_tree.json
echo   - test_summary.csv
echo.
echo Per visualizzare i risultati:
echo   - Apri test_traces.json in un editor di testo
echo   - Apri test_summary.csv in Excel
echo   - Esegui: python analyze_traces.py test_traces.json
echo.
echo Per usare con i tuoi modelli:
echo   generate_traces.bat tuo_modello.json
echo.

exit /b 0
