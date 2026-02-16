@echo off
REM ADO CLI wrapper script
REM This script activates the venv and calls the ado CLI
REM It preserves the caller's current directory for relative paths

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Activate the venv (located in project root, one level up from scripts/)
call "%SCRIPT_DIR%\..\.venv\Scripts\activate.bat"

REM Call the ado CLI with all arguments, staying in the caller's directory
python "%SCRIPT_DIR%\..\src\cli\ado.py" %*
