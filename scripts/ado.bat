@echo off
REM ADO CLI wrapper script
REM This script activates the venv and calls the ado CLI
REM It preserves the caller's current directory for relative paths

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Get the project root (one level up from scripts/)
set PROJECT_ROOT=%SCRIPT_DIR%\..

REM Set PYTHONPATH to include project root so Python can find the src module
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

REM Activate the venv
call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"

REM Call the ado CLI with all arguments, staying in the caller's directory
python "%PROJECT_ROOT%\src\cli\ado.py" %*
