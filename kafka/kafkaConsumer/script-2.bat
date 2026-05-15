@echo off
setlocal

:: Force the current working directory to the folder where this script lives
cd /d "%~dp0"

echo Running log analysis...
:: Navigate up one directory and into log-analyzer to execute scripts
python "..\log-analyzer\log-analyzer.py"
python "..\log-analyzer\visualize.py"

echo.
echo Analysis complete.

:: Automatically closes the window
exit