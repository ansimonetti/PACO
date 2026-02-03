@echo off
REM Mostra riepilogo dei file creati per il sistema di generazione tracce

echo.
echo ========================================================================
echo       SISTEMA GENERAZIONE E ANALISI TRACCE BPMN - FILE CREATI
echo ========================================================================
echo.
echo SCRIPT PRINCIPALI:
echo ==================
echo.
if exist "generate_all_traces.py" (
    echo [OK] generate_all_traces.py         - Genera tutte le tracce possibili
) else (
    echo [!!] generate_all_traces.py         - NON TROVATO
)
echo.
if exist "analyze_traces.py" (
    echo [OK] analyze_traces.py              - Analizza le tracce generate
) else (
    echo [!!] analyze_traces.py              - NON TROVATO
)
echo.
if exist "generate_traces.bat" (
    echo [OK] generate_traces.bat            - Script batch per generazione (Windows)
) else (
    echo [!!] generate_traces.bat            - NON TROVATO
)
echo.
if exist "analyze_traces.bat" (
    echo [OK] analyze_traces.bat             - Script batch per analisi (Windows)
) else (
    echo [!!] analyze_traces.bat             - NON TROVATO
)
echo.
if exist "test_trace_generation.bat" (
    echo [OK] test_trace_generation.bat      - Test rapido del sistema
) else (
    echo [!!] test_trace_generation.bat      - NON TROVATO
)
echo.
echo.
echo DOCUMENTAZIONE:
echo ===============
echo.
if exist "LEGGIMI_TRACCE.md" (
    echo [OK] LEGGIMI_TRACCE.md              - Guida completa in italiano
) else (
    echo [!!] LEGGIMI_TRACCE.md              - NON TROVATO
)
echo.
if exist "GENERATE_TRACES_README.md" (
    echo [OK] GENERATE_TRACES_README.md      - Guida dettagliata in inglese
) else (
    echo [!!] GENERATE_TRACES_README.md      - NON TROVATO
)
echo.
if exist "TRACES_SUMMARY.md" (
    echo [OK] TRACES_SUMMARY.md              - Riepilogo completo
) else (
    echo [!!] TRACES_SUMMARY.md              - NON TROVATO
)
echo.
if exist "CHECKLIST_TRACCE.md" (
    echo [OK] CHECKLIST_TRACCE.md            - Checklist rapida
) else (
    echo [!!] CHECKLIST_TRACCE.md            - NON TROVATO
)
echo.
echo.
echo FILE DI ESEMPIO:
echo ================
echo.
if exist "simple_test_model.json" (
    echo [OK] simple_test_model.json         - Modello BPMN semplice per test
) else (
    echo [!!] simple_test_model.json         - NON TROVATO
)
echo.
if exist "example_trace_analysis.ipynb" (
    echo [OK] example_trace_analysis.ipynb   - Notebook con esempio completo
) else (
    echo [!!] example_trace_analysis.ipynb   - NON TROVATO
)
echo.
echo.
echo UTILITY:
echo ========
echo.
if exist "show_files.bat" (
    echo [OK] show_files.bat                 - Questo script
) else (
    echo [!!] show_files.bat                 - NON TROVATO
)
echo.
echo ========================================================================
echo.
echo COMANDI RAPIDI:
echo ===============
echo.
echo Testare il sistema:
echo   test_trace_generation.bat
echo.
echo Generare tracce:
echo   generate_traces.bat modello.json
echo.
echo Analizzare tracce:
echo   analyze_traces.bat modello_traces.json
echo.
echo Aprire documentazione:
echo   start LEGGIMI_TRACCE.md
echo   start CHECKLIST_TRACCE.md
echo.
echo ========================================================================
echo.
pause
