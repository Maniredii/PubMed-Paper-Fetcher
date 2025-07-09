@echo off
echo ========================================
echo PubMed Paper Finder Application
echo ========================================
echo.
echo This application searches PubMed for research papers with industry authors.
echo.
echo Examples:
echo   1. Basic search: python cli.py main "cancer therapy"
echo   2. With options: python cli.py main "biotech drug discovery" --max-results 20 --debug
echo   3. Custom output: python cli.py main "pharmaceutical clinical trial" --file my_results.csv
echo.
echo Available options:
echo   --file (-f)        : Output CSV file name
echo   --max-results (-n) : Maximum number of papers (default: 20)
echo   --debug (-d)       : Show detailed filtering information
echo   --email (-e)       : Your email (recommended by NCBI)
echo   --detailed         : Export detailed report
echo   --help             : Show help
echo.
echo ========================================
echo.
pause
echo Enter your search query (or press Ctrl+C to exit):
set /p query="Query: "

if "%query%"=="" (
    echo No query entered. Exiting.
    pause
    exit /b
)

echo.
echo Running search for: %query%
echo.
python cli.py main "%query%" --max-results 15 --file results.csv

echo.
echo ========================================
echo Search completed! Check results.csv for output.
echo ========================================
pause
