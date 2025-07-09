@echo off
echo ========================================
echo PubMed Paper Finder - Setup
echo ========================================
echo.
echo Installing required Python packages...
echo.

pip install -r requirements.txt

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo You can now run the application in these ways:
echo.
echo 1. Interactive mode (easiest):
echo    python simple_run.py
echo.
echo 2. Command line mode:
echo    python cli.py main "your search query"
echo.
echo 3. Batch file (Windows):
echo    run_app.bat
echo.
echo ========================================
pause
