@echo off
REM Wrapper that lets you run "mercury" or "mercury go" from any folder in cmd/PowerShell.
REM %~dp0 = the folder this .bat file lives in, so mercury.py must sit
REM right next to mercury.bat (no manual path editing needed).
python "%~dp0mercury.py" %*
