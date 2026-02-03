@echo off
REM Genera execution tree e tracce per tutti i pattern di test

echo ========================================
echo GENERAZIONE EXECUTION TREE - TUTTI I PATTERN
echo ========================================
echo.

REM Prima esegui i test per generare i file JSON
echo [1/2] Esecuzione test per generare i pattern...
echo.
cd simulator\tests\spin
pytest exhaustiveness_test.py -v
if errorlevel 1 (
    echo.
    echo ERRORE: Test falliti
    cd ..\..\..
    pause
    exit /b 1
)
cd ..\..\..

echo.
echo ========================================
echo [2/2] Generazione execution tree per tutti i pattern...
echo ========================================
echo.

REM Poi genera gli execution tree
python generate_all_patterns.py

if errorlevel 1 (
    echo.
    echo ERRORE: Generazione fallita
    pause
    exit /b 1
)

echo.
echo ========================================
echo COMPLETATO!
echo ========================================
echo.
echo I risultati sono stati salvati in: generated_patterns\
echo.
exit /b 0
