@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0qaoa-maxcut.ps1" %*
exit /b %ERRORLEVEL%
