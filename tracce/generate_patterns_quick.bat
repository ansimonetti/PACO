@echo off
REM Genera execution tree per i pattern (assume che i JSON esistano già)

echo ========================================
echo GENERAZIONE EXECUTION TREE - QUICK MODE
echo ========================================
echo.
echo Questo script assume che i file JSON siano già
echo stati generati in simulator\tests\spin\output\
echo.
echo Se i file non esistono, usa generate_all_patterns.bat
echo ========================================
echo.

python generate_all_patterns.py %*

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
exit /b 0
