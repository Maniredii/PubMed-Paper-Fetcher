@echo off
REM Verification script for PDF requirements
echo ========================================
echo VERIFYING PDF REQUIREMENTS
echo ========================================

echo.
echo 1. Checking Poetry installation...
poetry --version
if %errorlevel% neq 0 (
    echo ERROR: Poetry not installed!
    echo Please install Poetry first.
    pause
    exit /b 1
)

echo.
echo 2. Installing dependencies with Poetry...
poetry install
if %errorlevel% neq 0 (
    echo ERROR: Poetry install failed!
    pause
    exit /b 1
)

echo.
echo 3. Testing get-papers-list command...
poetry run get-papers-list --help
if %errorlevel% neq 0 (
    echo ERROR: get-papers-list command failed!
    pause
    exit /b 1
)

echo.
echo 4. Testing with a sample query...
poetry run get-papers-list "test" --max-results 1
if %errorlevel% neq 0 (
    echo ERROR: Sample query failed!
    pause
    exit /b 1
)

echo.
echo 5. Checking Git repository...
git status
if %errorlevel% neq 0 (
    echo ERROR: Not a Git repository!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ALL REQUIREMENTS VERIFIED SUCCESSFULLY!
echo ========================================
echo.
echo ✅ Git: Repository initialized
echo ✅ Poetry: Dependencies installed
echo ✅ Executable: get-papers-list command works
echo.
echo Next step: Push to GitHub to complete all requirements
echo.
pause
