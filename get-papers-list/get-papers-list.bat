@echo off
REM Executable command for get-papers-list (Windows batch file)
REM This provides the get-papers-list command as required by the PDF specification

python "%~dp0cli.py" %*
