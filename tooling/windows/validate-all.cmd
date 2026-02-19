@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0validate-all.ps1" %*
exit /b %ERRORLEVEL%
