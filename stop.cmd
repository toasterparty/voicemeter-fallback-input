@echo off
set "script_dir=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy bypass -File "%script_dir%\ps1\stop.ps1"
