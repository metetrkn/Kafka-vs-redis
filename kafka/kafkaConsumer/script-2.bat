@echo off
setlocal

:: Force the current working directory to the folder where this script lives
cd /d "%~dp0"

echo Running log analysis...
:: Navigate up one directory and into log-analyzer to execute scripts
python "C:\Users\metet\Desktop\microservice-kafka-rqueue-mail-tests\kafka\log-analyzer\log-analyzer.py"
python "C:\Users\metet\Desktop\microservice-kafka-rqueue-mail-tests\kafka\log-analyzer\visualize.py"

echo.
echo Analysis complete.

:: Automatically closes the window
exit