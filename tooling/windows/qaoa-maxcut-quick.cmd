@echo off
setlocal
if "%~1"=="" (
	"%~dp0qaoa-maxcut.cmd" -Action evidence -Quick
) else (
	"%~dp0qaoa-maxcut.cmd" %*
)
exit /b %ERRORLEVEL%
