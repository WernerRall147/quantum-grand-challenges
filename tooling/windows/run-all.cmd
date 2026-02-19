@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-all.ps1" %*
exit /b %ERRORLEVEL%
